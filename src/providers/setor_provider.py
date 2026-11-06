from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.setor import Setor

class SetorProvider:
    @staticmethod
    async def get_all(session: AsyncSession) -> List[Setor]:
        result = await session.execute(select(Setor).order_by(Setor.nome))
        return result.scalars().all()

    @staticmethod
    async def get_by_id(session: AsyncSession, id: int) -> Optional[Setor]:
        result = await session.execute(select(Setor).where(Setor.id == id))
        return result.scalars().first()

    @staticmethod
    async def get_by_nome(session: AsyncSession, nome: str) -> Optional[Setor]:
        result = await session.execute(select(Setor).where(Setor.nome == nome))
        return result.scalars().first()

    @staticmethod
    async def create(session: AsyncSession, setor_data: dict, login: str) -> Setor:
        setor_data['login'] = login
        novo_setor = Setor(**setor_data)
        session.add(novo_setor)
        await session.flush()
        return novo_setor

    @staticmethod
    async def update(session: AsyncSession, id: int, setor_data: dict, login: str) -> Optional[Setor]:
        setor_data['login'] = login
        stmt = update(Setor).where(Setor.id == id).values(**setor_data).returning(Setor)
        result = await session.execute(stmt)
        await session.flush()
        return result.scalars().first()

    @staticmethod
    async def delete(session: AsyncSession, id: int) -> bool:
        stmt = delete(Setor).where(Setor.id == id)
        result = await session.execute(stmt)
        await session.flush()
        return result.rowcount > 0
