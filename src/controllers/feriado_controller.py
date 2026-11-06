from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.providers.feriado_provider import FeriadoProvider
from typing import Optional

class FeriadoController:
    @staticmethod
    async def get_all(session: AsyncSession, ano: Optional[int] = None):
        return await FeriadoProvider.get_all(session, ano)
        
    @staticmethod
    async def get_by_id(session: AsyncSession, id: int):
        feriado = await FeriadoProvider.get_by_id(session, id)
        if not feriado:
            raise HTTPException(status_code=404, detail="Feriado não encontrado.")
        return feriado

    @staticmethod
    async def create(session: AsyncSession, data: dict, login: str):
        if not data.get("nome") or not data.get("data") or not data.get("tipo"):
            raise HTTPException(status_code=400, detail="Nome, Data e Tipo são obrigatórios.")
            
        existente = await FeriadoProvider.get_by_data_e_nome(session, data["data"], data["nome"])
        if existente:
            raise HTTPException(status_code=400, detail="Já existe um feriado com este nome nesta data.")
            
        return await FeriadoProvider.create(session, data, login)

    @staticmethod
    async def update(session: AsyncSession, id: int, data: dict, login: str):
        feriado = await FeriadoProvider.get_by_id(session, id)
        if not feriado:
            raise HTTPException(status_code=404, detail="Feriado não encontrado.")
            
        # Check uniqueness if date or name changed
        nova_data = data.get("data", feriado.data)
        novo_nome = data.get("nome", feriado.nome)
        
        if nova_data != feriado.data or novo_nome != feriado.nome:
            existente = await FeriadoProvider.get_by_data_e_nome(session, nova_data, novo_nome)
            if existente and existente.id != id:
                raise HTTPException(status_code=400, detail="Já existe um feriado com este nome nesta data.")
                
        atualizado = await FeriadoProvider.update(session, id, data, login)
        return atualizado

    @staticmethod
    async def delete(session: AsyncSession, id: int):
        feriado = await FeriadoProvider.get_by_id(session, id)
        if not feriado:
            raise HTTPException(status_code=404, detail="Feriado não encontrado.")
            
        sucesso = await FeriadoProvider.delete(session, id)
        if not sucesso:
            raise HTTPException(status_code=500, detail="Erro ao excluir o feriado.")
        return {"message": "Feriado excluído com sucesso."}
