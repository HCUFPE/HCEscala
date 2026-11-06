from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from src.providers.divgp_provider import DivgpProvider

class DivgpController:
    @staticmethod
    async def get_status_unidades(session: AsyncSession, mes: int, ano: int, is_admin: bool = False) -> Dict[str, Any]:
        if not is_admin:
            raise HTTPException(status_code=403, detail="Acesso restrito à DIVGP e Administradores Gerais.")
        return await DivgpProvider.get_status_todas_unidades(session, mes, ano)

    @staticmethod
    async def get_faltantes(session: AsyncSession, unidade_id: int, mes: int, ano: int, is_admin: bool = False) -> List[Dict[str, Any]]:
        if not is_admin:
            raise HTTPException(status_code=403, detail="Acesso restrito à DIVGP e Administradores Gerais.")
        return await DivgpProvider.get_colaboradores_faltantes(session, unidade_id, mes, ano)

    @staticmethod
    async def get_todas_escalas(
        session: AsyncSession,
        mes: int,
        ano: int,
        uorg_id: Optional[int] = None,
        uorg_pai_id: Optional[int] = None,
        status: Optional[str] = None,
        cargo_id: Optional[int] = None,
        search: Optional[str] = None,
        is_admin: bool = False
    ) -> List[Dict[str, Any]]:
        if not is_admin:
            raise HTTPException(status_code=403, detail="Acesso restrito à DIVGP e Administradores Gerais.")
        return await DivgpProvider.get_todas_escalas(
            session=session,
            mes=mes,
            ano=ano,
            uorg_id=uorg_id,
            uorg_pai_id=uorg_pai_id,
            status_filter=status,
            cargo_id=cargo_id,
            search=search
        )

# Alias
DigpController = DivgpController
