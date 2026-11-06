from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.usuario_gerencia import UsuarioGerencia
from src.models.uorg import Uorg
from src.models.posto import Posto

class GerenciaProvider:
    @staticmethod
    async def get_all(
        session: AsyncSession, 
        nivel: Optional[str] = None, 
        uorg_id: Optional[int] = None, 
        apenas_ativos: bool = False
    ) -> List[UsuarioGerencia]:
        stmt = select(UsuarioGerencia).options(
            selectinload(UsuarioGerencia.uorg).selectinload(Uorg.uorg_pai),
            selectinload(UsuarioGerencia.posto).selectinload(Posto.uorg)
        ).order_by(UsuarioGerencia.nome)

        filters = []
        if nivel:
            filters.append(UsuarioGerencia.nivel == nivel)
        if uorg_id:
            filters.append(UsuarioGerencia.uorg_id == uorg_id)
        if apenas_ativos:
            filters.append(UsuarioGerencia.ativo == True)

        if filters:
            stmt = stmt.where(and_(*filters))

        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(session: AsyncSession, id: int) -> Optional[UsuarioGerencia]:
        stmt = select(UsuarioGerencia).options(
            selectinload(UsuarioGerencia.uorg).selectinload(Uorg.uorg_pai),
            selectinload(UsuarioGerencia.posto).selectinload(Posto.uorg)
        ).where(UsuarioGerencia.id == id)
        result = await session.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_by_usuario(session: AsyncSession, usuario: str) -> List[UsuarioGerencia]:
        stmt = select(UsuarioGerencia).options(
            selectinload(UsuarioGerencia.uorg).selectinload(Uorg.uorg_pai),
            selectinload(UsuarioGerencia.posto).selectinload(Posto.uorg)
        ).where(
            and_(
                UsuarioGerencia.usuario.ilike(usuario.strip()),
                UsuarioGerencia.ativo == True
            )
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def create(session: AsyncSession, data: dict, login: str) -> UsuarioGerencia:
        from ..helpers.audit_helper import registrar_log, model_to_dict
        data["login"] = login
        # Suporte a campos legados
        if "unidade_id" in data and "uorg_id" not in data:
            data["uorg_id"] = data.pop("unidade_id")
        if "setor_id" in data and "uorg_id" not in data:
            data["uorg_id"] = data.pop("setor_id")

        # Filtrar apenas campos existentes no modelo UsuarioGerencia
        allowed_fields = {"usuario", "nome", "nivel", "uorg_id", "posto_id", "ativo", "login"}
        clean_data = {k: v for k, v in data.items() if k in allowed_fields}

        novo = UsuarioGerencia(**clean_data)
        session.add(novo)
        await session.flush()

        try:
            await registrar_log(
                session=session,
                usuario=login,
                tela="Gerentes & Chefias",
                tabela="usuario_gerencias",
                operacao="INSERT",
                registro_id=novo.id,
                dados_anteriores=None,
                dados_posteriores=model_to_dict(novo)
            )
        except Exception as e_audit:
            print(f"Aviso ao registrar log de auditoria para gerência: {e_audit}")

        await session.commit()
        return await GerenciaProvider.get_by_id(session, novo.id)

    @staticmethod
    async def update(session: AsyncSession, id: int, data: dict, login: str) -> Optional[UsuarioGerencia]:
        from ..helpers.audit_helper import registrar_log, model_to_dict
        antigo = await GerenciaProvider.get_by_id(session, id)
        if not antigo:
            return None
        dados_ant = model_to_dict(antigo)

        data["login"] = login
        if "unidade_id" in data and "uorg_id" not in data:
            data["uorg_id"] = data.pop("unidade_id")
        if "setor_id" in data and "uorg_id" not in data:
            data["uorg_id"] = data.pop("setor_id")

        allowed_fields = {"usuario", "nome", "nivel", "uorg_id", "posto_id", "ativo", "login"}
        clean_data = {k: v for k, v in data.items() if k in allowed_fields}

        stmt = update(UsuarioGerencia).where(UsuarioGerencia.id == id).values(**clean_data)
        await session.execute(stmt)
        await session.flush()

        atualizado = await GerenciaProvider.get_by_id(session, id)
        dados_pos = model_to_dict(atualizado)

        try:
            await registrar_log(
                session=session,
                usuario=login,
                tela="Gerentes & Chefias",
                tabela="usuario_gerencias",
                operacao="UPDATE",
                registro_id=id,
                dados_anteriores=dados_ant,
                dados_posteriores=dados_pos
            )
        except Exception as e_audit:
            print(f"Aviso ao registrar log de auditoria no update da gerência: {e_audit}")

        await session.commit()
        return atualizado

    @staticmethod
    async def delete(session: AsyncSession, id: int) -> bool:
        from ..helpers.audit_helper import registrar_log, model_to_dict
        antigo = await GerenciaProvider.get_by_id(session, id)
        dados_ant = model_to_dict(antigo) if antigo else None
        login = getattr(antigo, "login", "sistema") if antigo else "sistema"

        stmt = delete(UsuarioGerencia).where(UsuarioGerencia.id == id)
        result = await session.execute(stmt)
        await session.flush()

        if result.rowcount > 0:
            try:
                await registrar_log(
                    session=session,
                    usuario=login,
                    tela="Gerentes & Chefias",
                    tabela="usuario_gerencias",
                    operacao="DELETE",
                    registro_id=id,
                    dados_anteriores=dados_ant,
                    dados_posteriores=None
                )
            except Exception as e_audit:
                print(f"Aviso ao registrar log de auditoria no delete da gerência: {e_audit}")

        await session.commit()
        return result.rowcount > 0

    @staticmethod
    async def get_user_scope(session: AsyncSession, usuario: str, user_groups: List[str] = None) -> Dict[str, Any]:
        """
        Resolve o escopo hierárquico de acesso do usuário atual.
        Retorna dicionário contendo o nível de autoridade e as UORGs/postos acessíveis.
        """
        user_groups = user_groups or []
        is_global_admin = (
            "GLO-SEC-HCPE-SETISD" in user_groups 
            or "DIVGP" in user_groups 
            or "DIGP" in user_groups 
            or usuario.lower() in ["admin", "root"]
        )

        gerencias = await GerenciaProvider.get_by_usuario(session, usuario)
        
        # Se tiver registro DIVGP_ADMIN / DIGP_ADMIN no banco ou pertencer ao grupo AD administrador
        if is_global_admin or any(g.nivel in ["DIVGP_ADMIN", "DIGP_ADMIN"] for g in gerencias):
            return {
                "usuario": usuario,
                "is_admin": True,
                "nivel": "DIVGP_ADMIN",
                "descricao_escopo": "Administrador Geral / DIVGP (Acesso Irrestrito)",
                "uorg_ids": None, # None = todas
                "unidade_ids": None,
                "posto_ids": None
            }

        if not gerencias:
            return {
                "usuario": usuario,
                "is_admin": False,
                "nivel": "COLABORADOR",
                "descricao_escopo": "Colaborador sem atribuição de gerência",
                "uorg_ids": [],
                "unidade_ids": [],
                "posto_ids": []
            }

        # Consolidar escopo de múltiplos registros de gerência do usuário (se houver)
        uorg_ids_set = set()
        posto_ids_set = set()
        maior_nivel = "COLABORADOR"

        for g in gerencias:
            if (g.nivel in ["UORG", "SETOR", "UNIDADE"]) and g.uorg_id:
                maior_nivel = "UORG" if maior_nivel not in ["DIVGP_ADMIN", "DIGP_ADMIN"] else maior_nivel
                uorg_ids_set.add(g.uorg_id)
                # Buscar todas as UORGs subordinadas em cascata (recursivo)
                queue = [g.uorg_id]
                while queue:
                    curr_id = queue.pop(0)
                    stmt_filhas = select(Uorg.id).where(Uorg.uorg_pai_id == curr_id)
                    res_f = await session.execute(stmt_filhas)
                    for fid in res_f.scalars().all():
                        if fid not in uorg_ids_set:
                            uorg_ids_set.add(fid)
                            queue.append(fid)

            elif g.nivel == "POSTO" and g.posto_id:
                if maior_nivel not in ["UORG", "SETOR", "UNIDADE", "DIVGP_ADMIN", "DIGP_ADMIN"]:
                    maior_nivel = "POSTO"
                posto_ids_set.add(g.posto_id)
                if g.posto and g.posto.uorg_id:
                    uorg_ids_set.add(g.posto.uorg_id)

        return {
            "usuario": usuario,
            "is_admin": False,
            "nivel": maior_nivel,
            "descricao_escopo": f"Gestão de Nível {maior_nivel}",
            "uorg_ids": list(uorg_ids_set),
            "unidade_ids": list(uorg_ids_set), # alias para compatibilidade
            "posto_ids": list(posto_ids_set) if posto_ids_set else None
        }

    @staticmethod
    async def is_top_level_manager(
        session: AsyncSession, 
        usuario: str, 
        uorg_id: int, 
        user_groups: List[str] = None
    ) -> bool:
        """
        Verifica se o usuário é o gestor do nível hierárquico mais alto para a UORG informada,
        sendo o único autorizado a homologar e liberar a escala para publicação pela DIVGP.
        Chefias subordinadas devem liberar para a UORG Superior imediata.
        """
        user_groups = user_groups or []
        if (
            "GLO-SEC-HCPE-SETISD" in user_groups 
            or "DIVGP" in user_groups 
            or "DIGP" in user_groups 
            or usuario.lower() in ["admin", "root"]
        ):
            return True

        gerencias = await GerenciaProvider.get_by_usuario(session, usuario)
        if any(g.nivel in ["DIVGP_ADMIN", "DIGP_ADMIN"] for g in gerencias):
            return True

        if not gerencias:
            return False

        # Obter a UORG da escala
        stmt = select(Uorg).where(Uorg.id == uorg_id)
        res = await session.execute(stmt)
        current_uorg = res.scalars().first()
        if not current_uorg:
            return False

        user_uorg_ids = set(g.uorg_id for g in gerencias if g.uorg_id and g.nivel in ["UORG", "SETOR", "UNIDADE"])

        # Se o usuário é gestor apenas no nível POSTO, ele nunca é top level da UORG
        if not user_uorg_ids:
            return False

        # 1. Se a UORG atual já é raiz (sem pai) e o usuário tem gestão direta dela
        if current_uorg.uorg_pai_id is None and current_uorg.id in user_uorg_ids:
            return True

        # 2. Rastrear a cadeia de ancestrais até o topo
        ancestor_ids = []
        curr_pai_id = current_uorg.uorg_pai_id
        while curr_pai_id is not None:
            ancestor_ids.append(curr_pai_id)
            stmt_p = select(Uorg).where(Uorg.id == curr_pai_id)
            res_p = await session.execute(stmt_p)
            p_obj = res_p.scalars().first()
            if not p_obj:
                break
            curr_pai_id = p_obj.uorg_pai_id

        # Se a UORG não tem ancestrais (é raiz)
        if not ancestor_ids:
            return current_uorg.id in user_uorg_ids

        # Se o usuário possui atribuição de gerência em QUALQUER ancestral superior (ex: Superintendência, Gerência de Atenção à Saúde, Divisão),
        # ele atua como autoridade hierárquica superior sobre a UORG e tem permissão para liberar para a DIVGP.
        for anc_id in ancestor_ids:
            if anc_id in user_uorg_ids:
                return True

        # Se o usuário é gestor apenas da própria UORG folha e nenhum superior da cadeia, ele é gestor subordinado
        return False
