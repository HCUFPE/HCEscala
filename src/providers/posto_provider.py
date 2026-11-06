from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.models.posto import Posto
from src.models.uorg import Uorg

class PostoProvider:
    @staticmethod
    async def get_all(session: AsyncSession) -> List[Posto]:
        stmt = select(Posto).options(
            selectinload(Posto.uorg).selectinload(Uorg.uorg_pai)
        ).order_by(Posto.nome)
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(session: AsyncSession, id: int) -> Optional[Posto]:
        stmt = select(Posto).options(
            selectinload(Posto.uorg).selectinload(Uorg.uorg_pai)
        ).where(Posto.id == id)
        result = await session.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_by_uorg(session: AsyncSession, uorg_id: int) -> List[Posto]:
        stmt = select(Posto).where(Posto.uorg_id == uorg_id).order_by(Posto.nome)
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_by_nome_and_uorg(session: AsyncSession, nome: str, uorg_id: int) -> Optional[Posto]:
        result = await session.execute(select(Posto).where(Posto.nome == nome, Posto.uorg_id == uorg_id))
        return result.scalars().first()

    @staticmethod
    async def create(session: AsyncSession, posto_data: dict, login: str) -> Posto:
        from datetime import datetime
        posto_data['login'] = login
        posto_data['data_alteracao'] = datetime.now()
        if 'nome' in posto_data:
            posto_data['nome'] = posto_data['nome'].strip().upper()
        
        target_id = posto_data.get('uorg_id') or posto_data.get('unidade_id')
        posto_data['uorg_id'] = target_id
        posto_data['unidade_id'] = target_id

        novo_posto = Posto(**posto_data)
        session.add(novo_posto)
        await session.commit()
        return await PostoProvider.get_by_id(session, novo_posto.id)

    @staticmethod
    async def update(session: AsyncSession, id: int, posto_data: dict, login: str) -> Optional[Posto]:
        from datetime import datetime
        posto_data['login'] = login
        posto_data['data_alteracao'] = datetime.now()
        if 'nome' in posto_data:
            posto_data['nome'] = posto_data['nome'].strip().upper()
        
        if 'uorg_id' in posto_data or 'unidade_id' in posto_data:
            target_id = posto_data.get('uorg_id') or posto_data.get('unidade_id')
            posto_data['uorg_id'] = target_id
            posto_data['unidade_id'] = target_id

        stmt = update(Posto).where(Posto.id == id).values(**posto_data)
        await session.execute(stmt)
        await session.commit()
        return await PostoProvider.get_by_id(session, id)

    @staticmethod
    async def delete(session: AsyncSession, id: int) -> bool:
        stmt = delete(Posto).where(Posto.id == id)
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0
