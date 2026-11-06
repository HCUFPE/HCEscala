from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.models.uorg import Uorg

class UorgProvider:
    @staticmethod
    async def get_all(session: AsyncSession) -> List[Uorg]:
        stmt = select(Uorg).options(
            selectinload(Uorg.uorg_pai),
            selectinload(Uorg.subordinadas),
            selectinload(Uorg.postos)
        ).order_by(Uorg.nome)
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_arvore(session: AsyncSession) -> List[Uorg]:
        stmt = select(Uorg).options(
            selectinload(Uorg.subordinadas).selectinload(Uorg.subordinadas),
            selectinload(Uorg.postos)
        ).where(Uorg.uorg_pai_id.is_(None)).order_by(Uorg.nome)
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(session: AsyncSession, id: int) -> Optional[Uorg]:
        stmt = select(Uorg).options(
            selectinload(Uorg.uorg_pai),
            selectinload(Uorg.subordinadas),
            selectinload(Uorg.postos)
        ).where(Uorg.id == id)
        result = await session.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_by_nome(session: AsyncSession, nome: str) -> Optional[Uorg]:
        stmt = select(Uorg).where(Uorg.nome == nome)
        result = await session.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def create(session: AsyncSession, data: dict, login: str) -> Uorg:
        from datetime import datetime
        from ..helpers.audit_helper import registrar_log, model_to_dict
        data['login'] = login
        data['data_alteracao'] = datetime.now()
        if 'nome' in data:
            data['nome'] = data['nome'].strip().upper()
        if 'codigo' in data and data['codigo']:
            data['codigo'] = data['codigo'].strip()
        if 'sigla' in data and data['sigla']:
            data['sigla'] = data['sigla'].strip().upper()

        novo = Uorg(**data)
        session.add(novo)
        await session.flush()

        await registrar_log(
            session=session,
            usuario=login,
            tela="Unidades Organizacionais",
            tabela="uorgs",
            operacao="INSERT",
            registro_id=novo.id,
            dados_anteriores=None,
            dados_posteriores=model_to_dict(novo)
        )
        await session.commit()
        await session.refresh(novo, ["uorg_pai", "subordinadas", "postos"])
        return novo

    @staticmethod
    async def update(session: AsyncSession, id: int, data: dict, login: str) -> Optional[Uorg]:
        from datetime import datetime
        from ..helpers.audit_helper import registrar_log, model_to_dict
        antigo = await UorgProvider.get_by_id(session, id)
        if not antigo:
            return None
        dados_ant = model_to_dict(antigo)

        data['login'] = login
        data['data_alteracao'] = datetime.now()
        if 'nome' in data:
            data['nome'] = data['nome'].strip().upper()
        if 'codigo' in data and data['codigo']:
            data['codigo'] = data['codigo'].strip()
        if 'sigla' in data and data['sigla']:
            data['sigla'] = data['sigla'].strip().upper()

        stmt = update(Uorg).where(Uorg.id == id).values(**data)
        await session.execute(stmt)
        await session.flush()

        atualizado = await UorgProvider.get_by_id(session, id)
        dados_pos = model_to_dict(atualizado)

        await registrar_log(
            session=session,
            usuario=login,
            tela="Unidades Organizacionais",
            tabela="uorgs",
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
        antigo = await UorgProvider.get_by_id(session, id)
        dados_ant = model_to_dict(antigo) if antigo else None
        login = getattr(antigo, "login", "sistema") if antigo else "sistema"

        stmt = delete(Uorg).where(Uorg.id == id)
        result = await session.execute(stmt)
        await session.flush()

        if result.rowcount > 0:
            await registrar_log(
                session=session,
                usuario=login,
                tela="Unidades Organizacionais",
                tabela="uorgs",
                operacao="DELETE",
                registro_id=id,
                dados_anteriores=dados_ant,
                dados_posteriores=None
            )
        await session.commit()
        return result.rowcount > 0

    @staticmethod
    async def get_descendant_ids(session: AsyncSession, root_id: int) -> List[int]:
        """
        Retorna uma lista com o ID da UORG fornecida e todos os IDs das UORGs
        subordinadas a ela (filhas, netas, etc.) em qualquer profundidade.
        """
        all_uorgs_stmt = select(Uorg.id, Uorg.uorg_pai_id)
        result = await session.execute(all_uorgs_stmt)
        rows = result.fetchall()
        
        # Mapeia pai -> [filhos]
        children_map = {}
        for uid, pai_id in rows:
            if pai_id is not None:
                children_map.setdefault(pai_id, []).append(uid)
                
        visited = []
        queue = [root_id]
        while queue:
            curr = queue.pop(0)
            visited.append(curr)
            for child in children_map.get(curr, []):
                if child not in visited and child not in queue:
                    queue.append(child)
                    
        return visited
