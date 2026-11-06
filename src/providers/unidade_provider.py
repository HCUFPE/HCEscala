from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.models.unidade import Unidade

class UnidadeProvider:
    @staticmethod
    async def get_all(session: AsyncSession) -> List[Unidade]:
        stmt = select(Unidade).options(selectinload(Unidade.setor)).order_by(Unidade.nome)
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(session: AsyncSession, id: int) -> Optional[Unidade]:
        stmt = select(Unidade).options(selectinload(Unidade.setor)).where(Unidade.id == id)
        result = await session.execute(stmt)
        return result.scalars().first()
        
    @staticmethod
    async def get_by_setor(session: AsyncSession, setor_id: int) -> List[Unidade]:
        stmt = select(Unidade).where(Unidade.setor_id == setor_id).order_by(Unidade.nome)
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_by_nome(session: AsyncSession, nome: str) -> Optional[Unidade]:
        result = await session.execute(select(Unidade).where(Unidade.nome == nome))
        return result.scalars().first()

    @staticmethod
    async def create(session: AsyncSession, unidade_data: dict, login: str) -> Unidade:
        unidade_data['login'] = login
        nova_unidade = Unidade(**unidade_data)
        session.add(nova_unidade)
        await session.flush()
        # Reload relationships
        await session.refresh(nova_unidade, ["setor"])
        return nova_unidade

    @staticmethod
    async def update(session: AsyncSession, id: int, unidade_data: dict, login: str) -> Optional[Unidade]:
        unidade_data['login'] = login
        stmt = update(Unidade).where(Unidade.id == id).values(**unidade_data)
        await session.execute(stmt)
        await session.flush()
        return await UnidadeProvider.get_by_id(session, id)

    @staticmethod
    async def delete(session: AsyncSession, id: int) -> bool:
        stmt = delete(Unidade).where(Unidade.id == id)
        result = await session.execute(stmt)
        await session.flush()
        return result.rowcount > 0
