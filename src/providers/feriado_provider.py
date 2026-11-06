from typing import List, Optional
from sqlalchemy import select, update, delete, extract
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.feriado import Feriado
from datetime import date

class FeriadoProvider:
    @staticmethod
    async def get_all(session: AsyncSession, ano: Optional[int] = None) -> List[Feriado]:
        stmt = select(Feriado).order_by(Feriado.data)
        if ano is not None:
            stmt = stmt.where(extract('year', Feriado.data) == ano)
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(session: AsyncSession, id: int) -> Optional[Feriado]:
        stmt = select(Feriado).where(Feriado.id == id)
        result = await session.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_by_data_e_nome(session: AsyncSession, data_feriado: date, nome: str) -> Optional[Feriado]:
        stmt = select(Feriado).where(Feriado.data == data_feriado, Feriado.nome == nome)
        result = await session.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def create(session: AsyncSession, data: dict, login: str) -> Feriado:
        from ..helpers.audit_helper import registrar_log, model_to_dict
        data['login'] = login
        novo = Feriado(**data)
        session.add(novo)
        await session.flush()

        await registrar_log(
            session=session,
            usuario=login,
            tela="Feriados",
            tabela="feriados",
            operacao="INSERT",
            registro_id=novo.id,
            dados_anteriores=None,
            dados_posteriores=model_to_dict(novo)
        )
        await session.commit()
        await session.refresh(novo)
        return novo

    @staticmethod
    async def update(session: AsyncSession, id: int, data: dict, login: str) -> Optional[Feriado]:
        from ..helpers.audit_helper import registrar_log, model_to_dict
        antigo = await FeriadoProvider.get_by_id(session, id)
        if not antigo:
            return None
        dados_ant = model_to_dict(antigo)

        data['login'] = login
        stmt = update(Feriado).where(Feriado.id == id).values(**data)
        await session.execute(stmt)
        await session.flush()

        atualizado = await FeriadoProvider.get_by_id(session, id)
        dados_pos = model_to_dict(atualizado)

        await registrar_log(
            session=session,
            usuario=login,
            tela="Feriados",
            tabela="feriados",
            operacao="UPDATE",
            registro_id=id,
            dados_anteriores=dados_ant,
            dados_posteriores=dados_pos
        )
        await session.commit()
        return atualizado

    @staticmethod
    async def delete(session: AsyncSession, id: int) -> bool:
        from ..helpers.audit_helper import registrar_log, model_to_dict
        antigo = await FeriadoProvider.get_by_id(session, id)
        dados_ant = model_to_dict(antigo) if antigo else None
        login = getattr(antigo, "login", "sistema") if antigo else "sistema"

        stmt = delete(Feriado).where(Feriado.id == id)
        result = await session.execute(stmt)
        await session.flush()

        if result.rowcount > 0:
            await registrar_log(
                session=session,
                usuario=login,
                tela="Feriados",
                tabela="feriados",
                operacao="DELETE",
                registro_id=id,
                dados_anteriores=dados_ant,
                dados_posteriores=None
            )
        await session.commit()
        return result.rowcount > 0
