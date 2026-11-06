from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.cargo import Cargo
from typing import List, Optional

class CargoProvider:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def listar(self) -> List[Cargo]:
        result = await self.session.execute(select(Cargo))
        return result.scalars().all()

    async def obter_por_id(self, id: int) -> Optional[Cargo]:
        result = await self.session.execute(select(Cargo).where(Cargo.id == id))
        return result.scalars().first()

    async def obter_por_nome(self, nome: str) -> Optional[Cargo]:
        from sqlalchemy import func
        clean_name = (nome or "").strip()
        result = await self.session.execute(
            select(Cargo).where(func.lower(func.trim(Cargo.nome)) == func.lower(clean_name))
        )
        return result.scalars().first()

    async def criar(self, data: dict) -> Cargo:
        from ..helpers.audit_helper import registrar_log, model_to_dict
        cargo = Cargo(**data)
        self.session.add(cargo)
        await self.session.flush()
        
        await registrar_log(
            session=self.session,
            usuario=data.get("login") or "sistema",
            tela="Cargos",
            tabela="cargos",
            operacao="INSERT",
            registro_id=cargo.id,
            dados_anteriores=None,
            dados_posteriores=model_to_dict(cargo)
        )
        await self.session.commit()
        return await self.obter_por_id(cargo.id)

    async def atualizar(self, id: int, data: dict) -> Optional[Cargo]:
        from ..helpers.audit_helper import registrar_log, model_to_dict
        from sqlalchemy import update
        cargo = await self.obter_por_id(id)
        if not cargo:
            return None
        
        dados_ant = model_to_dict(cargo)
        stmt = update(Cargo).where(Cargo.id == id).values(**data)
        await self.session.execute(stmt)
        await self.session.flush()

        atualizado = await self.obter_por_id(id)
        dados_pos = model_to_dict(atualizado) if atualizado else None

        await registrar_log(
            session=self.session,
            usuario=data.get("login") or "sistema",
            tela="Cargos",
            tabela="cargos",
            operacao="UPDATE",
            registro_id=id,
            dados_anteriores=dados_ant,
            dados_posteriores=dados_pos
        )
        await self.session.commit()
        return atualizado

    async def deletar(self, id: int) -> bool:
        from ..helpers.audit_helper import registrar_log, model_to_dict
        cargo = await self.obter_por_id(id)
        if not cargo:
            return False
            
        dados_ant = model_to_dict(cargo)
        login = getattr(cargo, "login", "sistema")
        await self.session.delete(cargo)
        await self.session.flush()

        await registrar_log(
            session=self.session,
            usuario=login,
            tela="Cargos",
            tabela="cargos",
            operacao="DELETE",
            registro_id=id,
            dados_anteriores=dados_ant,
            dados_posteriores=None
        )
        await self.session.commit()
        return True
