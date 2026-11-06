from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from src.providers.gerencia_provider import GerenciaProvider
from src.models.usuario_gerencia import UsuarioGerencia

class GerenciaController:
    @staticmethod
    async def get_all(
        session: AsyncSession, 
        nivel: Optional[str] = None, 
        uorg_id: Optional[int] = None, 
        apenas_ativos: bool = False
    ) -> List[UsuarioGerencia]:
        return await GerenciaProvider.get_all(session, nivel, uorg_id, apenas_ativos)

    @staticmethod
    async def get_by_id(session: AsyncSession, id: int) -> UsuarioGerencia:
        gerencia = await GerenciaProvider.get_by_id(session, id)
        if not gerencia:
            raise HTTPException(status_code=404, detail="Atribuição de gerência não encontrada.")
        return gerencia

    @staticmethod
    async def get_my_scope(session: AsyncSession, username: str, user_groups: List[str] = None) -> Dict[str, Any]:
        return await GerenciaProvider.get_user_scope(session, username, user_groups)

    @staticmethod
    def _validate_payload(data: dict):
        nivel = data.get("nivel")
        if not nivel or nivel not in ["DIVGP_ADMIN", "DIGP_ADMIN", "UORG", "SETOR", "UNIDADE", "POSTO"]:
            raise HTTPException(status_code=400, detail="Nível de gerência inválido. Opções permitidas: DIVGP_ADMIN, UORG, POSTO.")

        if not data.get("usuario") or not data.get("usuario").strip():
            raise HTTPException(status_code=400, detail="O usuário (login de rede) é obrigatório.")

        if not data.get("nome") or not data.get("nome").strip():
            raise HTTPException(status_code=400, detail="O nome do gestor é obrigatório.")

        if nivel in ["UORG", "SETOR", "UNIDADE"]:
            uorg_id = data.get("uorg_id") or data.get("unidade_id") or data.get("setor_id")
            if not uorg_id:
                raise HTTPException(status_code=400, detail="A Unidade Organizacional (uorg_id) é obrigatória para o nível UORG.")
            data["uorg_id"] = uorg_id
            data["nivel"] = "UORG"

        if nivel == "POSTO" and not data.get("posto_id"):
            raise HTTPException(status_code=400, detail="O posto_id é obrigatório para o nível POSTO.")

    @staticmethod
    async def create(session: AsyncSession, data: dict, login: str, is_admin: bool = False) -> UsuarioGerencia:
        if not is_admin:
            raise HTTPException(status_code=403, detail="Apenas administradores da DIVGP podem atribuir gerências a usuários.")
        
        GerenciaController._validate_payload(data)
        return await GerenciaProvider.create(session, data, login)

    @staticmethod
    async def update(session: AsyncSession, id: int, data: dict, login: str, is_admin: bool = False) -> UsuarioGerencia:
        if not is_admin:
            raise HTTPException(status_code=403, detail="Apenas administradores da DIVGP podem editar atribuições de gerência.")
        
        gerencia = await GerenciaProvider.get_by_id(session, id)
        if not gerencia:
            raise HTTPException(status_code=404, detail="Atribuição de gerência não encontrada.")

        GerenciaController._validate_payload(data)
        return await GerenciaProvider.update(session, id, data, login)

    @staticmethod
    async def delete(session: AsyncSession, id: int, is_admin: bool = False) -> Dict[str, Any]:
        if not is_admin:
            raise HTTPException(status_code=403, detail="Apenas administradores da DIVGP podem remover atribuições de gerência.")

        gerencia = await GerenciaProvider.get_by_id(session, id)
        if not gerencia:
            raise HTTPException(status_code=404, detail="Atribuição de gerência não encontrada.")

        sucesso = await GerenciaProvider.delete(session, id)
        if not sucesso:
            raise HTTPException(status_code=500, detail="Erro ao excluir a atribuição de gerência.")
        return {"message": "Atribuição de gerência excluída com sucesso."}
