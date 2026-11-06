from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.models.funcionario import Funcionario
from src.models.funcionario_lotacao import FuncionarioLotacao
from src.models.funcionario_ferias import FuncionarioFerias

class FuncionarioProvider:
    @staticmethod
    async def get_all(session: AsyncSession) -> List[Funcionario]:
        stmt = select(Funcionario).options(
            selectinload(Funcionario.cargo),
            selectinload(Funcionario.escala),
            selectinload(Funcionario.vinculo),
            selectinload(Funcionario.lotacoes).selectinload(FuncionarioLotacao.uorg),
            selectinload(Funcionario.lotacoes).selectinload(FuncionarioLotacao.posto),
            selectinload(Funcionario.ferias)
        ).order_by(Funcionario.nome)
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(session: AsyncSession, id: int) -> Optional[Funcionario]:
        stmt = select(Funcionario).options(
            selectinload(Funcionario.cargo),
            selectinload(Funcionario.escala),
            selectinload(Funcionario.vinculo),
            selectinload(Funcionario.lotacoes).selectinload(FuncionarioLotacao.uorg),
            selectinload(Funcionario.lotacoes).selectinload(FuncionarioLotacao.posto),
            selectinload(Funcionario.ferias)
        ).where(Funcionario.id == id)
        result = await session.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_by_matricula(session: AsyncSession, matricula: str) -> Optional[Funcionario]:
        stmt = select(Funcionario).options(
            selectinload(Funcionario.cargo),
            selectinload(Funcionario.escala),
            selectinload(Funcionario.vinculo)
        ).where(Funcionario.matricula == matricula)
        result = await session.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def create(session: AsyncSession, data: dict, login: str) -> Funcionario:
        from ..helpers.audit_helper import registrar_log, model_to_dict
        data['login'] = login
        novo = Funcionario(**data)
        session.add(novo)
        await session.flush()

        await registrar_log(
            session=session,
            usuario=login,
            tela="Funcionários",
            tabela="funcionarios",
            operacao="INSERT",
            registro_id=novo.id,
            dados_anteriores=None,
            dados_posteriores=model_to_dict(novo)
        )
        await session.commit()
        await session.refresh(novo, ["cargo", "escala", "vinculo", "lotacoes", "ferias"])
        return novo

    @staticmethod
    async def update(session: AsyncSession, id: int, data: dict, login: str) -> Optional[Funcionario]:
        from ..helpers.audit_helper import registrar_log, model_to_dict
        antigo = await FuncionarioProvider.get_by_id(session, id)
        if not antigo:
            return None
        dados_ant = model_to_dict(antigo)

        data['login'] = login
        stmt = update(Funcionario).where(Funcionario.id == id).values(**data)
        await session.execute(stmt)
        await session.flush()

        atualizado = await FuncionarioProvider.get_by_id(session, id)
        dados_pos = model_to_dict(atualizado)

        await registrar_log(
            session=session,
            usuario=login,
            tela="Funcionários",
            tabela="funcionarios",
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
        antigo = await FuncionarioProvider.get_by_id(session, id)
        dados_ant = model_to_dict(antigo) if antigo else None
        login = getattr(antigo, "login", "sistema") if antigo else "sistema"

        stmt = delete(Funcionario).where(Funcionario.id == id)
        result = await session.execute(stmt)
        await session.flush()

        if result.rowcount > 0:
            await registrar_log(
                session=session,
                usuario=login,
                tela="Funcionários",
                tabela="funcionarios",
                operacao="DELETE",
                registro_id=id,
                dados_anteriores=dados_ant,
                dados_posteriores=None
            )
        await session.commit()
        return result.rowcount > 0

    @staticmethod
    async def add_lotacao(session: AsyncSession, funcionario_id: int, data: dict, login: str) -> FuncionarioLotacao:
        data['funcionario_id'] = funcionario_id
        data['login'] = login
        
        # Sincroniza uorg_id a partir de unidade_id se fornecido
        uorg_val = data.get('uorg_id') or data.get('unidade_id')
        if uorg_val:
            data['uorg_id'] = int(uorg_val)
            
        # Remover campos extras e propriedades antes de instanciar o modelo SQLAlchemy
        data.pop('unidade_id', None)
        data.pop('uorg', None)
        data.pop('unidade', None)
        data.pop('posto', None)

        nova_lotacao = FuncionarioLotacao(**data)
        session.add(nova_lotacao)
        await session.commit()
        await session.refresh(nova_lotacao, ["uorg", "posto"])
        return nova_lotacao

    @staticmethod
    async def update_lotacao(session: AsyncSession, id: int, data: dict, login: str) -> Optional[FuncionarioLotacao]:
        data['login'] = login
        
        # Sincroniza uorg_id se fornecido
        if 'uorg_id' in data or 'unidade_id' in data:
            uorg_val = data.get('uorg_id') or data.get('unidade_id')
            data['uorg_id'] = int(uorg_val) if uorg_val else None
            
        data.pop('unidade_id', None)
        data.pop('uorg', None)
        data.pop('unidade', None)
        data.pop('posto', None)

        stmt = update(FuncionarioLotacao).where(FuncionarioLotacao.id == id).values(**data)
        await session.execute(stmt)
        await session.commit()
        
        # Carregar com relacionamentos
        res = await session.execute(
            select(FuncionarioLotacao).options(
                selectinload(FuncionarioLotacao.uorg),
                selectinload(FuncionarioLotacao.posto)
            ).where(FuncionarioLotacao.id == id)
        )
        return res.scalars().first()

    @staticmethod
    async def remove_lotacao(session: AsyncSession, id: int) -> bool:
        stmt = delete(FuncionarioLotacao).where(FuncionarioLotacao.id == id)
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0

    @staticmethod
    async def ajustar_inicio_lotacoes_abertas(session: AsyncSession, nova_data_inicio: str, login: str) -> int:
        from datetime import datetime, date
        dt_obj = date.fromisoformat(nova_data_inicio) if isinstance(nova_data_inicio, str) else nova_data_inicio
        stmt = (
            update(FuncionarioLotacao)
            .where(FuncionarioLotacao.data_fim.is_(None))
            .values(
                data_inicio=dt_obj,
                login=login,
                data_alteracao=datetime.now()
            )
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount

    @staticmethod
    async def add_ferias(session: AsyncSession, funcionario_id: int, data: dict, login: str) -> FuncionarioFerias:
        data['funcionario_id'] = funcionario_id
        data['login'] = login
        novas_ferias = FuncionarioFerias(**data)
        session.add(novas_ferias)
        await session.commit()
        return novas_ferias

    @staticmethod
    async def remove_ferias(session: AsyncSession, id: int) -> bool:
        stmt = delete(FuncionarioFerias).where(FuncionarioFerias.id == id)
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0
