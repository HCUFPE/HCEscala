from typing import List, Dict, Any, Optional
from datetime import date
import calendar
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.uorg import Uorg
from src.models.funcionario import Funcionario
from src.models.funcionario_lotacao import FuncionarioLotacao
from src.models.grade import Grade
from src.models.cargo import Cargo

class DivgpProvider:
    @staticmethod
    async def get_status_todas_unidades(
        session: AsyncSession, 
        mes: int, 
        ano: int
    ) -> Dict[str, Any]:
        """
        Gera relatório institucional de status de homologação de grades para a DIVGP.
        Retorna o sumário consolidado do hospital e a listagem detalhada por UORG / UORG Pai.
        """
        _, last_day = calendar.monthrange(ano, mes)
        start_of_month = date(ano, mes, 1)
        end_of_month = date(ano, mes, last_day)

        # 1. Buscar todas as UORGs com suas UORGs Pai
        stmt_uorgs = (
            select(Uorg)
            .options(selectinload(Uorg.uorg_pai))
            .order_by(Uorg.nome)
        )
        res_uorgs = await session.execute(stmt_uorgs)
        uorgs = res_uorgs.scalars().all()

        # 2. Buscar todas as lotações ativas no mês
        stmt_lotacoes = (
            select(FuncionarioLotacao)
            .options(
                selectinload(FuncionarioLotacao.funcionario)
            )
            .where(
                and_(
                    FuncionarioLotacao.data_inicio <= end_of_month,
                    or_(
                        FuncionarioLotacao.data_fim.is_(None),
                        FuncionarioLotacao.data_fim >= start_of_month
                    )
                )
            )
        )
        res_lot = await session.execute(stmt_lotacoes)
        todas_lotacoes = res_lot.scalars().all()

        lotacoes_por_uorg: Dict[int, List[FuncionarioLotacao]] = {}
        for l in todas_lotacoes:
            target_id = l.uorg_id or l.unidade_id
            if target_id:
                lotacoes_por_uorg.setdefault(target_id, []).append(l)

        # 3. Buscar todas as grades cadastradas no mês/ano
        stmt_grades = (
            select(Grade)
            .where(
                and_(
                    Grade.mes == mes,
                    Grade.ano == ano
                )
            )
        )
        res_grades = await session.execute(stmt_grades)
        todas_grades = res_grades.scalars().all()

        grades_por_uorg: Dict[int, List[Grade]] = {}
        for g in todas_grades:
            target_id = g.uorg_id or g.unidade_id
            if target_id:
                grades_por_uorg.setdefault(target_id, []).append(g)

        # 4. Consolidar métricas por UORG
        detalhes_unidades = []
        total_colab_hospital = 0
        total_pub_hospital = 0
        total_unidades_100 = 0
        total_unidades_pendentes = 0

        for u in uorgs:
            lotacoes_unid = lotacoes_por_uorg.get(u.id, [])
            grades_unid = grades_por_uorg.get(u.id, [])

            func_ids_lotados = set(l.funcionario_id for l in lotacoes_unid if l.funcionario_id)
            total_colab = len(func_ids_lotados)

            # Omitir da listagem UORGs que não possuem colaboradores vinculados no mês
            if total_colab == 0:
                continue

            grades_map = {g.funcionario_id: g for g in grades_unid}
            
            total_pub = sum(1 for g in grades_unid if g.status == "Publicada")
            total_pend = sum(1 for g in grades_unid if g.status in ["Rascunho", "Enviada", "Aprovada"])
            
            # Sem grade = colaboradores lotados que não possuem registro de grade na UORG
            total_sem_grade = sum(1 for fid in func_ids_lotados if fid not in grades_map)

            pct = round((total_pub / total_colab) * 100, 1) if total_colab > 0 else 100.0

            if total_pub == total_colab:
                status_homolog = "HOMOLOGADA_100"
                total_unidades_100 += 1
            elif total_pub > 0 or total_pend > 0:
                status_homolog = "PARCIAL"
                total_unidades_pendentes += 1
            else:
                status_homolog = "SEM_ENVIO"
                total_unidades_pendentes += 1

            total_colab_hospital += total_colab
            total_pub_hospital += total_pub

            uorg_pai_nome = u.uorg_pai.nome if u.uorg_pai else "Nível Raiz"

            detalhes_unidades.append({
                "uorg_id": u.id,
                "uorg_nome": u.nome,
                "uorg_pai_id": u.uorg_pai_id,
                "uorg_pai_nome": uorg_pai_nome,
                # Compatibilidade legada
                "unidade_id": u.id,
                "unidade_nome": u.nome,
                "setor_id": u.uorg_pai_id,
                "setor_nome": uorg_pai_nome,
                "total_colaboradores": total_colab,
                "total_publicadas": total_pub,
                "total_pendentes": total_pend,
                "total_sem_grade": total_sem_grade,
                "percentual_conclusao": pct,
                "status_homologacao": status_homolog
            })

        pct_geral = round((total_pub_hospital / total_colab_hospital) * 100, 1) if total_colab_hospital > 0 else 100.0

        return {
            "mes": mes,
            "ano": ano,
            "sumario": {
                "total_unidades": len(detalhes_unidades),
                "unidades_100": total_unidades_100,
                "unidades_pendentes": total_unidades_pendentes,
                "total_colaboradores_hospital": total_colab_hospital,
                "total_grades_publicadas_hospital": total_pub_hospital,
                "percentual_geral_hospital": pct_geral,
                "total_colaboradores": total_colab_hospital,
                "total_publicadas": total_pub_hospital,
                "percentual_geral": pct_geral
            },
            "unidades": detalhes_unidades
        }

    @staticmethod
    async def get_colaboradores_sem_escala(
        session: AsyncSession, 
        mes: int, 
        ano: int, 
        uorg_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retorna a listagem nominal de todos os colaboradores do hospital (ou de uma UORG)
        que não possuem grade publicada no mês de referência.
        """
        _, last_day = calendar.monthrange(ano, mes)
        start_of_month = date(ano, mes, 1)
        end_of_month = date(ano, mes, last_day)

        # 1. Obter lotações ativas
        stmt_lot = (
            select(FuncionarioLotacao)
            .options(
                selectinload(FuncionarioLotacao.funcionario).selectinload(Funcionario.cargo),
                selectinload(FuncionarioLotacao.funcionario).selectinload(Funcionario.escala),
                selectinload(FuncionarioLotacao.uorg).selectinload(Uorg.uorg_pai),
                selectinload(FuncionarioLotacao.posto)
            )
            .where(
                and_(
                    FuncionarioLotacao.data_inicio <= end_of_month,
                    or_(
                        FuncionarioLotacao.data_fim.is_(None),
                        FuncionarioLotacao.data_fim >= start_of_month
                    )
                )
            )
        )
        if uorg_id:
            stmt_lot = stmt_lot.where(FuncionarioLotacao.uorg_id == uorg_id)

        res_lot = await session.execute(stmt_lot)
        lotacoes = res_lot.scalars().all()

        # 2. Obter grades publicadas no mês
        stmt_pub = (
            select(Grade.funcionario_id, Grade.uorg_id)
            .where(
                and_(
                    Grade.mes == mes,
                    Grade.ano == ano,
                    Grade.status == "Publicada"
                )
            )
        )
        res_pub = await session.execute(stmt_pub)
        grades_pub_set = set((row[0], row[1]) for row in res_pub.all())

        # 3. Filtrar os que NÃO têm grade publicada
        resultado = []
        vistos = set()

        for l in lotacoes:
            f = l.funcionario
            if not f:
                continue

            target_uorg_id = l.uorg_id
            chave = (f.id, target_uorg_id)
            if chave in vistos:
                continue
            vistos.add(chave)

            if chave not in grades_pub_set:
                uorg_obj = l.uorg
                uorg_nome = uorg_obj.nome if uorg_obj else "Sem UORG"
                uorg_pai_nome = (uorg_obj.uorg_pai.nome if (uorg_obj and uorg_obj.uorg_pai) else "Geral")

                resultado.append({
                    "funcionario_id": f.id,
                    "matricula": f.matricula,
                    "nome": f.nome,
                    "cargo": f.cargo.nome if f.cargo else "Não informado",
                    "codigo_escala": f.escala.codigo if f.escala else "Sem Escala",
                    "uorg_id": target_uorg_id,
                    "uorg_nome": uorg_nome,
                    "uorg_pai_nome": uorg_pai_nome,
                    # Compatibilidade legada
                    "unidade_id": target_uorg_id,
                    "unidade_nome": uorg_nome,
                    "setor_nome": uorg_pai_nome,
                    "posto_nome": l.posto.nome if l.posto else "Geral"
                })

        resultado.sort(key=lambda x: (x["uorg_nome"], x["nome"]))
        return resultado

    # Alias de compatibilidade
    get_colaboradores_faltantes = get_colaboradores_sem_escala

    @staticmethod
    async def get_todas_escalas(
        session: AsyncSession,
        mes: int,
        ano: int,
        uorg_id: Optional[int] = None,
        uorg_pai_id: Optional[int] = None,
        status_filter: Optional[str] = None,
        cargo_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retorna a listagem nominal de todas as escalas e colaboradores do hospital com seus respectivos status.
        Permite filtros combinados por UORG, UORG Pai, Status, Cargo e termo de busca.
        """
        from src.providers.grade_provider import GradeProvider
        from src.models.grade import GradeDia

        _, last_day = calendar.monthrange(ano, mes)
        start_of_month = date(ano, mes, 1)
        end_of_month = date(ano, mes, last_day)

        # 1. Buscar todas as lotações ativas no mês
        stmt_lot = (
            select(FuncionarioLotacao)
            .options(
                selectinload(FuncionarioLotacao.funcionario).selectinload(Funcionario.cargo),
                selectinload(FuncionarioLotacao.funcionario).selectinload(Funcionario.escala),
                selectinload(FuncionarioLotacao.uorg).selectinload(Uorg.uorg_pai),
                selectinload(FuncionarioLotacao.posto)
            )
            .where(
                and_(
                    FuncionarioLotacao.data_inicio <= end_of_month,
                    or_(
                        FuncionarioLotacao.data_fim.is_(None),
                        FuncionarioLotacao.data_fim >= start_of_month
                    )
                )
            )
        )
        res_lot = await session.execute(stmt_lot)
        todas_lotacoes = res_lot.scalars().all()

        # 2. Buscar todas as grades do mês/ano
        stmt_grades = (
            select(Grade)
            .options(
                selectinload(Grade.dias).selectinload(GradeDia.escala)
            )
            .where(
                and_(
                    Grade.mes == mes,
                    Grade.ano == ano
                )
            )
        )
        res_grades = await session.execute(stmt_grades)
        todas_grades = res_grades.scalars().all()

        grades_map: Dict[tuple, Grade] = {}
        for g in todas_grades:
            grades_map[(g.funcionario_id, g.uorg_id)] = g

        itens = []
        processados = set()

        # Processar lotações
        for l in todas_lotacoes:
            f = l.funcionario
            if not f:
                continue

            target_uorg = l.uorg
            target_uorg_id = l.uorg_id or (target_uorg.id if target_uorg else None)
            chave = (f.id, target_uorg_id)
            if chave in processados:
                continue
            processados.add(chave)

            grade = grades_map.get(chave)

            # Filtro por UORG
            if uorg_id and target_uorg_id != uorg_id:
                continue

            # Filtro por UORG Pai
            if uorg_pai_id:
                if not target_uorg or target_uorg.uorg_pai_id != uorg_pai_id:
                    continue

            # Filtro por Cargo
            if cargo_id and f.cargo_id != cargo_id:
                continue

            # Filtro por Busca (Nome ou Matrícula)
            if search:
                term = search.strip().lower()
                if term not in f.nome.lower() and term not in (f.matricula or "").lower():
                    continue

            # Determinar status da escala
            grade_status = grade.status if grade else "Sem Escala"

            # Filtro por Status
            if status_filter and status_filter.upper() != "TODOS":
                if status_filter.upper() == "SEM_ESCALA" and grade_status != "Sem Escala":
                    continue
                elif status_filter.upper() != "SEM_ESCALA" and grade_status != status_filter:
                    continue

            # Cálculos de Carga Horária
            carga_semanal = getattr(f, "carga_horaria", None) or 40
            escala_sigla = (f.escala.sigla.upper() if f.escala and f.escala.sigla else "")
            escala_codigo = (f.escala.codigo.upper() if f.escala and f.escala.codigo else "")
            is_diarista = (
                (f.escala and not f.escala.apenas_assistenciais)
                or any(term in escala_sigla for term in ["DIARISTA", "5X2", "ADM", "SEG-SEX", "40H", "30H", "20H"])
                or ("DIARISTA" in escala_codigo)
            )
            dias_uteis = sum(1 for dia_i in range(1, last_day + 1) if date(ano, mes, dia_i).weekday() < 5)
            total_horas = 0.0
            if grade and grade.dias:
                siglas_grade = [d.legenda_sigla for d in grade.dias if d.legenda_sigla]
                horas_diarista = GradeProvider.obter_horas_diarista_colaborador(
                    siglas_grade,
                    escala_sigla,
                    carga_semanal
                )
                if horas_diarista > 0:
                    is_diarista = True
                elif any((s or "").strip().upper() in GradeProvider.TURNOS_PLANTONISTA_MAP for s in siglas_grade):
                    is_diarista = False
                elif is_diarista:
                    horas_diarista = round(carga_semanal / 5.0, 1)

                total_horas = sum(
                    GradeProvider.calcular_horas_turno(
                        d.legenda_sigla,
                        d.escala,
                        horas_diarista=horas_diarista,
                        horas_ferias_dia=(
                            (horas_diarista if horas_diarista > 0 else round(carga_semanal / 5.0, 1))
                            if (1 <= d.dia <= last_day and date(ano, mes, d.dia).weekday() < 5)
                            else 0.0
                        ),
                        is_dia_util_semana=(1 <= d.dia <= last_day and date(ano, mes, d.dia).weekday() < 5)
                    )
                    for d in grade.dias
                )
            ch_teto = GradeProvider.calcular_teto_mensal(carga_semanal, last_day, dias_uteis, is_diarista)

            saldo_horas = round(ch_teto - total_horas, 1)

            uorg_nome = target_uorg.nome if target_uorg else "Sem UORG"
            uorg_pai_nome = target_uorg.uorg_pai.nome if (target_uorg and target_uorg.uorg_pai) else "Nível Raiz"

            itens.append({
                "funcionario_id": f.id,
                "matricula": f.matricula,
                "nome": f.nome,
                "cargo": f.cargo.nome if f.cargo else "Não informado",
                "cargo_id": f.cargo_id,
                "codigo_escala": f.escala.codigo if f.escala else "-",
                "escala_padrao": f.escala.sigla if f.escala else "-",
                "uorg_id": target_uorg_id,
                "uorg_nome": uorg_nome,
                "uorg_pai_id": target_uorg.uorg_pai_id if target_uorg else None,
                "uorg_pai_nome": uorg_pai_nome,
                "posto_id": l.posto_id,
                "posto_nome": l.posto.nome if l.posto else "Geral",
                "grade_id": grade.id if grade else None,
                "grade_status": grade_status,
                "observacao": grade.observacao if grade else None,
                "login_responsavel": grade.login if grade else None,
                "data_alteracao": grade.data_alteracao.isoformat() if (grade and grade.data_alteracao) else None,
                "carga_horaria_semanal": carga_semanal,
                "carga_horaria_mensal_teto": ch_teto,
                "total_horas_escaladas": total_horas,
                "saldo_horas": saldo_horas,
                "is_diarista": is_diarista
            })

        itens.sort(key=lambda x: (x["uorg_pai_nome"], x["uorg_nome"], x["nome"]))
        return itens
