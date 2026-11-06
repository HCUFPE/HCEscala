from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from ..models.escala import Escala
from typing import List, Optional

class EscalaProvider:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def listar(self) -> List[Escala]:
        result = await self.session.execute(select(Escala))
        return result.scalars().all()

    async def obter_por_id(self, id: int) -> Optional[Escala]:
        result = await self.session.execute(select(Escala).where(Escala.id == id))
        return result.scalars().first()

    async def obter_por_codigo(self, codigo: str) -> Optional[Escala]:
        result = await self.session.execute(select(Escala).where(Escala.codigo == codigo))
        return result.scalars().first()

    async def obter_por_sigla(self, sigla: str) -> Optional[Escala]:
        result = await self.session.execute(select(Escala).where(Escala.sigla == sigla))
        return result.scalars().first()

    async def criar(self, data: dict) -> Escala:
        from ..helpers.audit_helper import registrar_log, model_to_dict
        escala = Escala(**data)
        self.session.add(escala)
        await self.session.flush()

        await registrar_log(
            session=self.session,
            usuario=data.get("login") or "sistema",
            tela="Códigos de Escala",
            tabela="escalas",
            operacao="INSERT",
            registro_id=escala.id,
            dados_anteriores=None,
            dados_posteriores=model_to_dict(escala)
        )
        await self.session.commit()
        await self.session.refresh(escala)
        return escala

    async def atualizar(self, id: int, data: dict) -> Optional[Escala]:
        from ..helpers.audit_helper import registrar_log, model_to_dict
        escala = await self.obter_por_id(id)
        if not escala:
            return None
        
        dados_ant = model_to_dict(escala)
        for key, value in data.items():
            setattr(escala, key, value)
            
        await self.session.flush()
        dados_pos = model_to_dict(escala)

        await registrar_log(
            session=self.session,
            usuario=data.get("login") or "sistema",
            tela="Códigos de Escala",
            tabela="escalas",
            operacao="UPDATE",
            registro_id=escala.id,
            dados_anteriores=dados_ant,
            dados_posteriores=dados_pos
        )
        await self.session.commit()
        await self.session.refresh(escala)
        return escala

    async def deletar(self, id: int) -> bool:
        from ..helpers.audit_helper import registrar_log, model_to_dict
        escala = await self.obter_por_id(id)
        if not escala:
            return False
        
        dados_ant = model_to_dict(escala)
        login = getattr(escala, "login", "sistema")
        await self.session.delete(escala)
        await self.session.flush()

        await registrar_log(
            session=self.session,
            usuario=login,
            tela="Códigos de Escala",
            tabela="escalas",
            operacao="DELETE",
            registro_id=id,
            dados_anteriores=dados_ant,
            dados_posteriores=None
        )
        await self.session.commit()
        return True
