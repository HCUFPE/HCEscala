from typing import List, Optional, Dict, Any
from datetime import date
import calendar
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.grade import Grade, GradeDia
from src.models.funcionario import Funcionario
from src.models.funcionario_lotacao import FuncionarioLotacao
from src.models.funcionario_ferias import FuncionarioFerias
from src.models.feriado import Feriado
from src.models.cargo import Cargo
from src.models.escala import Escala
from src.models.uorg import Uorg
from src.models.unidade import Unidade
from src.models.posto import Posto

class GradeProvider:
    # Mapeamento de turnos de diaristas (em horas trabalhadas por dia)
    TURNOS_DIARISTA_MAP: Dict[str, float] = {
        "M8": 4.0, "M10": 4.0, "M26": 4.0, "T10": 4.0, "T11": 4.0,
        "T25": 4.0, "T26": 4.0, "T27": 4.0, "N11": 4.0, "M4": 4.0, "T4": 4.0, "4H": 4.0, "FE4": 4.0,
        "P5H7I": 5.0, "5H": 5.0, "FE5": 5.0,
        "M": 6.0, "M6": 6.0, "MANHA": 6.0, "M15": 6.0, "M17": 6.0,
        "T": 6.0, "T6": 6.0, "TARDE": 6.0, "T15": 6.0, "T17": 6.0,
        "T18": 6.0, "T19": 6.0, "T28": 6.0, "TN2": 6.0, "TN3": 6.0, "TN4": 6.0,
        "AFIN6": 6.0, "FD6": 6.0, "FE6": 6.0, "6H": 6.0,
        "AFIN7": 7.0, "7H": 7.0, "FE7": 7.0,
        "MT": 8.0, "MT1": 8.0, "MT2": 8.0, "MT3": 8.0, "MT4": 8.0, "MT5": 8.0,
        "MT6": 8.0, "MT7": 8.0, "MT8": 8.0, "MT11": 8.0, "MT12": 8.0, "MT13": 8.0,
        "MT16": 8.0, "MT22": 8.0, "MT23": 8.0, "MT24": 8.0, "MT25": 8.0,
        "MT26": 8.0, "MT27": 8.0, "MT28": 8.0, "MT29": 8.0, "MT30": 8.0,
        "MT47": 8.0, "MT49": 8.0,
        "ADM": 8.0, "D8": 8.0, "8H": 8.0, "P8H13I": 8.0, "P8H14I": 8.0,
        "PM8H7": 8.0, "PM8H8": 8.0, "AFIN8": 8.0, "FD8": 8.0, "FE8": 8.0,
    }

    # Mapeamento de turnos de plantonistas (em horas trabalhadas por plantão)
    TURNOS_PLANTONISTA_MAP: Dict[str, float] = {
        "PM10H7": 10.0, "PM10H8": 10.0, "10H": 10.0, "FE10": 10.0,
        "D": 12.0, "D6": 12.0, "SD": 12.0, "DIA": 12.0, "DIURNO": 12.0,
        "P12D": 12.0, "12X36": 12.0, "P12": 12.0,
        "N": 12.0, "N8": 12.0, "SN": 12.0, "NOITE": 12.0, "P12N": 12.0, "12H": 12.0,
        "FE12": 12.0, "FE12D": 12.0, "FE12N": 12.0,
        "M16": 16.0, "PMHD16": 16.0, "16H": 16.0, "FE16": 16.0,
        "PM18H7": 18.0, "PM18H8": 18.0, "18H": 18.0, "FE18": 18.0,
        "PM20H7": 20.0, "PM20H8": 20.0, "20H": 20.0, "FE20": 20.0,
        "PM1": 24.0, "P24": 24.0, "24H": 24.0, "FE24": 24.0,
    }

    @staticmethod
    def obter_horas_diarista_colaborador(
        siglas: List[Optional[str]],
        escala_padrao: Optional[str] = None,
        carga_horaria_semanal: int = 40
    ) -> float:
        """
        Determina a carga horária diária de diarista do colaborador com base nos turnos
        alocados na grade (ou escala padrão).
        Retorna > 0.0 quando o colaborador atua como diarista, ou 0.0 quando é plantonista (12h/24h).
        """
        contagem_horas: Dict[float, int] = {}
        qtd_diarista = 0
        qtd_plantonista = 0
        tem_feriado_ou_ferias = False

        codigos_auxiliares_diarista = {"FD", "FD0", "FD6", "FD8", "FE4", "FE5", "FE6", "FE7", "FE8"}
        codigos_auxiliares_plantonista = {"FE10", "FE12", "FE12D", "FE12N", "FE16", "FE18", "FE20", "FE24"}

        for s in siglas:
            if not s:
                continue
            s_up = s.strip().upper()
            if s_up in GradeProvider.TURNOS_PLANTONISTA_MAP:
                qtd_plantonista += 1
            elif s_up in GradeProvider.TURNOS_DIARISTA_MAP and s_up not in codigos_auxiliares_diarista:
                h = GradeProvider.TURNOS_DIARISTA_MAP[s_up]
                contagem_horas[h] = contagem_horas.get(h, 0) + 1
                qtd_diarista += 1
            elif s_up in ("FR", "FD", "FD0", "FD6", "FD8", "FER", "FERIADO", "FE", "FERIAS", "FÉRIAS") or s_up in codigos_auxiliares_diarista:
                tem_feriado_ou_ferias = True

        # Se o colaborador possui turnos de plantonista (ex: D6, N8) em maior ou igual quantidade que diarista, é plantonista
        if qtd_plantonista > 0 and qtd_plantonista >= qtd_diarista:
            return 0.0

        # Se possui turnos efetivos de diarista na grade, usa a duração predominante
        if contagem_horas:
            return max(contagem_horas.items(), key=lambda item: item[1])[0]

        # Se a escala padrão do cadastro for explicitamente de diarista (sem confundir D6/D de 12h)
        if escala_padrao:
            esc_up = escala_padrao.strip().upper()
            if esc_up in GradeProvider.TURNOS_DIARISTA_MAP:
                return GradeProvider.TURNOS_DIARISTA_MAP[esc_up]
            if any(term in esc_up for term in ["DIARISTA", "5X2", "ADM", "SEG-SEX", "40H", "30H", "20H"]):
                return round(carga_horaria_semanal / 5.0, 1)

        # Se possui apenas férias/feriados na grade e nenhum plantão 12h/24h
        if tem_feriado_ou_ferias and qtd_plantonista == 0:
            if carga_horaria_semanal >= 40:
                return 8.0
            if carga_horaria_semanal <= 20:
                return 4.0
            return 6.0

        return 0.0

    @staticmethod
    def calcular_horas_turno(
        sigla: Optional[str],
        escala: Optional[Escala] = None,
        horas_diarista: float = 0.0,
        horas_ferias_dia: float = 0.0,
        is_dia_util_semana: bool = True
    ) -> float:
        """
        Calcula as horas trabalhadas para uma determinada sigla/escala.
        - Para Diarista (horas_diarista > 0): Feriado (FR, FD, FD0, FD6, FER) e Férias (FE)
          em dias de semana (seg-sex) contabilizam a jornada diária do diarista.
        - Para Plantonista (horas_diarista == 0): Feriado sem plantão (FR, FD0) conta 0h,
          e quando há plantão no dia do feriado (ex: D6, N8) conta normalmente as horas do plantão.
        """
        if not sigla:
            return 0.0
        sigla_upper = sigla.strip().upper()

        # Folga diarista compensada com carga explícita
        if sigla_upper == "FD6":
            return float(horas_diarista) if (horas_diarista > 0 and is_dia_util_semana) else (6.0 if is_dia_util_semana else 0.0)
        if sigla_upper == "FD8":
            return float(horas_diarista) if (horas_diarista > 0 and is_dia_util_semana) else (8.0 if is_dia_util_semana else 0.0)

        # Marcação de feriado (FR, FD, FD0, FER, FERIADO):
        # Para diarista em dia de semana (seg-sex), contabiliza horas_diarista; para plantonista ou fim de semana, 0h.
        if sigla_upper in ["FR", "FD", "FD0", "FER", "FERIADO"]:
            if horas_diarista > 0 and is_dia_util_semana:
                return float(horas_diarista)
            return 0.0

        # Férias genéricas (FE): contabiliza horas_ferias_dia quando em dia de semana
        if sigla_upper in ["FE", "FERIAS", "FÉRIAS"]:
            if is_dia_util_semana and horas_ferias_dia > 0:
                return float(horas_ferias_dia)
            return 0.0

        # Mapeamentos padronizados de turnos de diaristas e plantonistas (inclui FE6, FE8, FE12, FE12D, etc.)
        if sigla_upper in GradeProvider.TURNOS_DIARISTA_MAP:
            return GradeProvider.TURNOS_DIARISTA_MAP[sigla_upper]
        if sigla_upper in GradeProvider.TURNOS_PLANTONISTA_MAP:
            return GradeProvider.TURNOS_PLANTONISTA_MAP[sigla_upper]

        # Folgas, Afastamentos, Compensações e Abonos -> 0h
        if (
            sigla_upper in ["F", "FOLGA", "LM", "LP", "A", "FJ", "LIC", "PC1"]
            or sigla_upper.startswith("FOLGA")
            or sigla_upper.startswith("CH")
            or sigla_upper.startswith("AB")
        ):
            return 0.0

        # Se houver objeto de escala com horários definidos
        if escala and escala.inicio_jornada and escala.fim_jornada:
            ini = escala.inicio_jornada
            fim = escala.fim_jornada
            ini_min = ini.hour * 60 + ini.minute
            fim_min = fim.hour * 60 + fim.minute
            if fim_min == ini_min:
                return 24.0 if "24" in (escala.descricao or "") else 0.0
            if fim_min > ini_min:
                horas_calc = (fim_min - ini_min) / 60.0
            else:  # cruza meia-noite (ex: 19h às 07h -> 12h)
                horas_calc = (24 * 60 - ini_min + fim_min) / 60.0
            # Tolerância de 15 minutos de ponto (ex: 07:00 às 13:15 -> 6.0h)
            if abs(horas_calc - round(horas_calc)) <= 0.25:
                return float(round(horas_calc))
            return round(horas_calc, 1)

        return 6.0

    @staticmethod
    def calcular_teto_mensal(carga_horaria_semanal: int, total_dias_mes: int, dias_uteis: int, is_diarista: bool) -> float:
        """
        Calcula a carga horária mensal máxima contratual do colaborador.
        """
        if is_diarista:
            # Diaristas: dias úteis x (carga semanal / 5)
            horas_dia = carga_horaria_semanal / 5.0
            return round(dias_uteis * horas_dia, 1)
        else:
            # Plantonistas / Geral: proporcional às semanas do mês (CH semanal * dias / 7)
            # ex: 40h/sem em mês de 31 dias -> 177.1h (~14 plantões de 12h = 168h)
            # ex: 30h/sem em mês de 31 dias -> 132.9h (~11 plantões de 12h = 132h)
            return round((carga_horaria_semanal * total_dias_mes) / 7.0, 1)

    @staticmethod
    async def get_by_id(session: AsyncSession, id: int) -> Optional[Grade]:
        stmt = select(Grade).options(
            selectinload(Grade.funcionario).selectinload(Funcionario.cargo),
            selectinload(Grade.funcionario).selectinload(Funcionario.escala),
            selectinload(Grade.uorg).selectinload(Uorg.uorg_pai),
            selectinload(Grade.posto),
            selectinload(Grade.dias).selectinload(GradeDia.escala)
        ).where(Grade.id == id)
        result = await session.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_by_funcionario_unidade_mes_ano(
        session: AsyncSession, 
        funcionario_id: int, 
        unidade_id: int, 
        mes: int, 
        ano: int
    ) -> Optional[Grade]:
        stmt = select(Grade).options(
            selectinload(Grade.dias).selectinload(GradeDia.escala)
        ).where(
            and_(
                Grade.funcionario_id == funcionario_id,
                Grade.uorg_id == unidade_id,
                Grade.mes == mes,
                Grade.ano == ano
            )
        )
        result = await session.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_matrix_data(
        session: AsyncSession,
        unidade_id: Optional[int],
        mes: int,
        ano: int,
        cargo_id: Optional[int] = None,
        search_term: Optional[str] = None,
        status_filter: Optional[str] = None,
        apenas_publicadas: bool = False,
        posto_id: Optional[int] = None,
        incluir_subordinadas: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retorna a lista consolidada de colaboradores lotados na unidade (ou geral se sem unidade),
        com suas grades mensais preenchidas (se houver), férias no período e outras lotações.
        Se apenas_publicadas for True (visão DIVGP.), apenas grades com status 'Publicada' são exibidas.
        Se incluir_subordinadas for True e unidade_id fornecida, busca em todas as UORGs filhas hierarquicamente.
        """
        _, last_day = calendar.monthrange(ano, mes)
        start_of_month = date(ano, mes, 1)
        end_of_month = date(ano, mes, last_day)

        target_uorg_ids = []
        if unidade_id:
            if incluir_subordinadas:
                from src.providers.uorg_provider import UorgProvider
                target_uorg_ids = await UorgProvider.get_descendant_ids(session, unidade_id)
            else:
                target_uorg_ids = [unidade_id]

        # 1. Buscar Funcionários com lotação ativa na unidade/posto no mês OU com grade salva na unidade/posto no mês
        func_ids_in_unit = []
        if target_uorg_ids or posto_id:
            lotacao_subqueries = [
                FuncionarioLotacao.data_inicio <= end_of_month,
                or_(
                    FuncionarioLotacao.data_fim.is_(None),
                    FuncionarioLotacao.data_fim >= start_of_month
                )
            ]
            if target_uorg_ids:
                lotacao_subqueries.append(FuncionarioLotacao.uorg_id.in_(target_uorg_ids))
            if posto_id:
                lotacao_subqueries.append(FuncionarioLotacao.posto_id == posto_id)

            stmt_lotacoes = (
                select(FuncionarioLotacao.funcionario_id)
                .where(and_(*lotacao_subqueries))
                .distinct()
            )
            result_lotacoes = await session.execute(stmt_lotacoes)
            lot_ids = set(result_lotacoes.scalars().all())

            grade_subqueries = [
                Grade.mes == mes,
                Grade.ano == ano
            ]
            if target_uorg_ids:
                grade_subqueries.append(Grade.uorg_id.in_(target_uorg_ids))
            if posto_id:
                grade_subqueries.append(Grade.posto_id == posto_id)

            stmt_grades_func = (
                select(Grade.funcionario_id)
                .where(and_(*grade_subqueries))
                .distinct()
            )
            result_grades_func = await session.execute(stmt_grades_func)
            grade_func_ids = set(result_grades_func.scalars().all())

            func_ids_in_unit = list(lot_ids.union(grade_func_ids))

            if not func_ids_in_unit:
                return []

        # 1.1 Buscar Feriados cadastrados no mês/ano
        stmt_feriados = (
            select(Feriado)
            .where(
                and_(
                    Feriado.data >= start_of_month,
                    Feriado.data <= end_of_month
                )
            )
        )
        result_feriados = await session.execute(stmt_feriados)
        feriados_mes = result_feriados.scalars().all()
        feriados_map = {f.data.day: f.nome for f in feriados_mes}

        # 2. Buscar dados completos dos funcionários
        func_filters = []
        if unidade_id or posto_id:
            func_filters.append(Funcionario.id.in_(func_ids_in_unit))
        if cargo_id:
            func_filters.append(Funcionario.cargo_id == cargo_id)
        if search_term:
            term = f"%{search_term.strip()}%"
            func_filters.append(
                or_(
                    Funcionario.nome.ilike(term),
                    Funcionario.matricula.ilike(term)
                )
            )

        stmt_funcs = (
            select(Funcionario)
            .options(
                selectinload(Funcionario.cargo),
                selectinload(Funcionario.escala),
                selectinload(Funcionario.lotacoes).selectinload(FuncionarioLotacao.uorg),
                selectinload(Funcionario.lotacoes).selectinload(FuncionarioLotacao.posto),
                selectinload(Funcionario.ferias)
            )
            .order_by(Funcionario.nome)
        )
        if func_filters:
            stmt_funcs = stmt_funcs.where(and_(*func_filters))

        result_funcs = await session.execute(stmt_funcs)
        funcionarios = result_funcs.scalars().all()

        if not funcionarios:
            return []

        all_func_ids = [f.id for f in funcionarios]

        # 3. Buscar todas as grades existentes para esses funcionários no mês/ano (todas as unidades para detectar turnos cruzados)
        stmt_grades = (
            select(Grade)
            .options(
                selectinload(Grade.dias).selectinload(GradeDia.escala),
                selectinload(Grade.uorg),
                selectinload(Grade.posto)
            )
            .where(
                and_(
                    Grade.funcionario_id.in_(all_func_ids),
                    Grade.mes == mes,
                    Grade.ano == ano
                )
            )
        )
        result_grades = await session.execute(stmt_grades)
        all_grades_list = result_grades.scalars().all()

        grades_by_func = {}
        for g in all_grades_list:
            grades_by_func.setdefault(g.funcionario_id, []).append(g)

        # 4. Montar a resposta matricial
        matrix_items = []
        for func_obj in funcionarios:
            func_grades = grades_by_func.get(func_obj.id, [])

            # Lotações ativas do funcionário no mês
            lotacoes_ativas = [
                lot for lot in func_obj.lotacoes
                if lot.data_inicio <= end_of_month and (lot.data_fim is None or lot.data_fim >= start_of_month)
            ]
            has_multiple_lotacoes = len(lotacoes_ativas) > 1

            # Determinar a lotação atual com base nos filtros
            if posto_id and target_uorg_ids:
                lotacao_atual = next((l for l in lotacoes_ativas if l.posto_id == posto_id and l.uorg_id in target_uorg_ids), None)
            elif posto_id:
                lotacao_atual = next((l for l in lotacoes_ativas if l.posto_id == posto_id), None)
            elif target_uorg_ids:
                lotacao_atual = next((l for l in lotacoes_ativas if l.uorg_id in target_uorg_ids), None)
            else:
                lotacao_atual = lotacoes_ativas[0] if lotacoes_ativas else None

            # Determinar a grade atual e outras grades
            if target_uorg_ids:
                if posto_id:
                    grade_atual = next((g for g in func_grades if g.uorg_id in target_uorg_ids and g.posto_id == posto_id), None)
                    # Não usar fallback para grades de outros postos quando um posto específico foi selecionado
                else:
                    grade_atual = next((g for g in func_grades if g.uorg_id in target_uorg_ids), None)
                outras_grades = [g for g in func_grades if g.id != (grade_atual.id if grade_atual else None)]
            else:
                if posto_id:
                    grade_atual = next((g for g in func_grades if g.posto_id == posto_id), None)
                else:
                    grade_atual = func_grades[0] if func_grades else None
                outras_grades = [g for g in func_grades if g.id != (grade_atual.id if grade_atual else None)]

            # Regra DIVGP: Se visualização restrita a publicadas, apenas grades com status 'Publicada' são exibidas
            if apenas_publicadas:
                if grade_atual and grade_atual.status != "Publicada":
                    grade_atual = None
                outras_grades = [g for g in outras_grades if g.status == "Publicada"]

            # Filtro por status
            status_atual = grade_atual.status if grade_atual else "Pendente"
            if status_filter and status_filter != "Todos":
                if status_filter == "Pendente" and grade_atual is not None:
                    continue
                elif status_filter != "Pendente" and (not grade_atual or grade_atual.status != status_filter):
                    continue

            # Filtro por posto (aplicar no resultado final para garantir correspondência exata se houver)
            if posto_id:
                grade_posto = grade_atual.posto_id if grade_atual else None
                lot_posto = lotacao_atual.posto_id if lotacao_atual else None
                # Se nem a grade atual nem a lotação correspondem ao posto_id, verificar se possui em alguma lotação ativa
                has_posto = (grade_posto == posto_id or lot_posto == posto_id or any(l.posto_id == posto_id for l in lotacoes_ativas))
                if not has_posto:
                    continue

            # Identificação de Colaborador Diarista (ex: 5x2, 40h/30h, não apenas assistencial, sem plantão 12x36)
            escala_sigla = (func_obj.escala.sigla.upper() if func_obj.escala and func_obj.escala.sigla else "")
            escala_codigo = (func_obj.escala.codigo.upper() if func_obj.escala and func_obj.escala.codigo else "")
            is_diarista = (
                (func_obj.escala and not func_obj.escala.apenas_assistenciais and escala_sigla not in GradeProvider.TURNOS_PLANTONISTA_MAP)
                or any(term in escala_sigla for term in ["DIARISTA", "5X2", "ADM", "SEG-SEX", "40H", "30H", "20H"])
                or ("DIARISTA" in escala_codigo)
            )

            # Férias ativas no mês
            ferias_no_mes = [
                feria for feria in func_obj.ferias
                if feria.data_inicio <= end_of_month and feria.data_fim >= start_of_month
            ]

            lotacoes_info = [
                {
                    "unidade_id": l.uorg_id,
                    "unidade_nome": l.uorg.nome if l.uorg else "Unidade",
                    "posto_id": l.posto_id,
                    "posto_nome": l.posto.nome if l.posto else "Geral",
                    "is_atual": (l.uorg_id in target_uorg_ids) if target_uorg_ids else False
                }
                for l in lotacoes_ativas
            ]

            posto_nome = lotacao_atual.posto.nome if lotacao_atual and lotacao_atual.posto else "Geral"
            resolved_posto_id = lotacao_atual.posto_id if lotacao_atual else (grade_atual.posto_id if grade_atual else None)

            # Dias da grade atual
            dias_map_atual = {d.dia: d for d in grade_atual.dias} if grade_atual else {}

            # Cálculo de Carga Horária Semanal e Horas Diarista do Colaborador
            carga_horaria_semanal = getattr(func_obj, "carga_horaria", None) or (func_obj.cargo.carga_horaria if hasattr(func_obj.cargo, 'carga_horaria') else 40)
            todas_siglas_func = [d.legenda_sigla for d in (grade_atual.dias if grade_atual else []) if d.legenda_sigla]
            for og in outras_grades:
                todas_siglas_func.extend([od.legenda_sigla for od in og.dias if od.legenda_sigla])

            horas_diarista = GradeProvider.obter_horas_diarista_colaborador(
                siglas=todas_siglas_func,
                escala_padrao=escala_sigla,
                carga_horaria_semanal=carga_horaria_semanal
            )
            if horas_diarista > 0:
                is_diarista = True
            elif any((s or "").strip().upper() in GradeProvider.TURNOS_PLANTONISTA_MAP for s in todas_siglas_func):
                is_diarista = False
            elif is_diarista:
                horas_diarista = round(carga_horaria_semanal / 5.0, 1)

            # Dias das outras unidades/postos (para divisão de carga horária e visualização de alocações externas)
            dias_map_outras = {}
            for og in outras_grades:
                if og.posto and og.posto.nome:
                    unid_nome = f"{og.posto.nome}"
                elif og.uorg and og.uorg.nome:
                    unid_nome = f"{og.uorg.nome}"
                else:
                    unid_nome = "Outro Posto/Unidade"

                for od in og.dias:
                    if od.legenda_sigla:
                        existing_other = dias_map_outras.get(od.dia)
                        # Prioriza turnos efetivos de trabalho sobre marcações de feriado/folga em outros postos
                        if existing_other:
                            old_s = (existing_other["sigla"] or "").strip().upper()
                            new_s = od.legenda_sigla.strip().upper()
                            if old_s not in ("FR", "FD", "FD0", "FER", "FERIADO", "F", "FE") and new_s in ("FR", "FD", "FD0", "FER", "FERIADO", "F", "FE"):
                                continue
                        dias_map_outras[od.dia] = {
                            "sigla": od.legenda_sigla,
                            "escala": od.escala,
                            "unidade_nome": unid_nome,
                            "descricao": od.descricao
                        }

            dias_list = []
            for dia_num in range(1, last_day + 1):
                dia_date = date(ano, mes, dia_num)
                is_ferias = any(f.data_inicio <= dia_date <= f.data_fim for f in ferias_no_mes)
                feriado_nome = feriados_map.get(dia_num)
                is_feriado = (feriado_nome is not None)

                outra_info = dias_map_outras.get(dia_num)
                outra_unidade_sigla = outra_info["sigla"] if outra_info else None
                outra_unidade_escala = outra_info.get("escala") if outra_info else None
                outra_unidade_nome = outra_info["unidade_nome"] if outra_info else None

                dia_item = dias_map_atual.get(dia_num)
                if dia_item:
                    sigla = dia_item.legenda_sigla
                    escala_id = dia_item.escala_id
                    descricao = dia_item.descricao or (f"Feriado: {feriado_nome}" if is_feriado else None)
                elif is_ferias:
                    sigla = "FE"
                    escala_id = None
                    descricao = "Férias"
                elif outra_unidade_sigla is not None:
                    sigla = None
                    escala_id = None
                    descricao = None
                elif is_diarista and horas_diarista > 0 and is_feriado and dia_date.weekday() < 5 and (grade_atual is not None or len(outras_grades) > 0 or len(ferias_no_mes) > 0):
                    # Para colaborador diarista, feriado em dia útil (seg-sex) contabiliza como dia de feriado (FR)
                    sigla = "FR"
                    escala_id = None
                    descricao = f"Feriado: {feriado_nome}"
                else:
                    sigla = None
                    escala_id = None
                    descricao = f"Feriado: {feriado_nome}" if is_feriado else None

                # Se na unidade atual está apenas como FR/FD0 mas no outro posto o colaborador trabalhou num turno efetivo (plantonista ou diarista)
                if (
                    sigla and sigla.strip().upper() in ("FR", "FD0")
                    and outra_unidade_sigla
                    and outra_unidade_sigla.strip().upper() not in ("FR", "FD", "FD0", "FER", "FERIADO", "F", "FE")
                ):
                    sigla = None
                    escala_id = None

                is_outra_unidade = (sigla is None and outra_unidade_sigla is not None)

                if is_outra_unidade:
                    descricao = f"Alocado em {outra_unidade_nome} ({outra_unidade_sigla})"

                is_dia_util_semana = (dia_date.weekday() < 5)
                horas_ferias_dia = (
                    (horas_diarista if horas_diarista > 0 else round(carga_horaria_semanal / 5.0, 1))
                    if is_dia_util_semana
                    else 0.0
                )

                horas = GradeProvider.calcular_horas_turno(
                    sigla,
                    dia_item.escala if dia_item else None,
                    horas_diarista=horas_diarista,
                    horas_ferias_dia=horas_ferias_dia,
                    is_dia_util_semana=is_dia_util_semana
                )

                dias_list.append({
                    "dia": dia_num,
                    "sigla": sigla,
                    "escala_id": escala_id,
                    "descricao": descricao,
                    "horas": horas,
                    "is_ferias": is_ferias,
                    "is_feriado": is_feriado,
                    "feriado_nome": feriado_nome,
                    "outra_unidade_sigla": outra_unidade_sigla,
                    "outra_unidade_nome": outra_unidade_nome,
                    "is_outra_unidade": is_outra_unidade
                })

            # Cálculo de Carga Horária Mensal:
            # Para diarista, como feriados e férias em dias de semana (seg-sex) são contabilizados nas horas,
            # todos os dias de seg-sex do mês entram em dias_uteis_no_mes.
            dias_uteis_no_mes = sum(
                1 for d_item in dias_list
                if date(ano, mes, d_item["dia"]).weekday() < 5
                and (
                    is_diarista
                    or d_item["dia"] not in feriados_map
                    or d_item["horas"] > 0
                    or (
                        d_item["is_outra_unidade"]
                        and GradeProvider.calcular_horas_turno(
                            d_item["outra_unidade_sigla"],
                            horas_diarista=horas_diarista,
                            is_dia_util_semana=True
                        ) > 0
                    )
                )
            )
            carga_horaria_mensal_teto = GradeProvider.calcular_teto_mensal(
                carga_horaria_semanal=carga_horaria_semanal,
                total_dias_mes=last_day,
                dias_uteis=dias_uteis_no_mes,
                is_diarista=is_diarista
            )

            total_horas_unidade = sum(d["horas"] for d in dias_list if not d["is_outra_unidade"])
            total_horas_outras = sum(
                GradeProvider.calcular_horas_turno(
                    d["outra_unidade_sigla"],
                    dias_map_outras[d["dia"]].get("escala") if d["dia"] in dias_map_outras else None,
                    horas_diarista=horas_diarista,
                    horas_ferias_dia=(
                        (horas_diarista if horas_diarista > 0 else round(carga_horaria_semanal / 5.0, 1))
                        if (date(ano, mes, d["dia"]).weekday() < 5)
                        else 0.0
                    ),
                    is_dia_util_semana=(date(ano, mes, d["dia"]).weekday() < 5)
                )
                for d in dias_list if d["is_outra_unidade"]
            )
            total_horas_escaladas = round(total_horas_unidade + total_horas_outras, 1)
            ultrapassou_ch = (total_horas_escaladas > carga_horaria_mensal_teto)
            horas_excedentes = max(0.0, round(total_horas_escaladas - carga_horaria_mensal_teto, 1))
            saldo_ch = round(carga_horaria_mensal_teto - total_horas_escaladas, 1)

            matrix_items.append({
                "funcionario_id": func_obj.id,
                "matricula": func_obj.matricula,
                "nome": func_obj.nome,
                "cargo": func_obj.cargo.nome if func_obj.cargo else "-",
                "cargo_id": func_obj.cargo_id,
                "unidade_id": grade_atual.uorg_id if grade_atual else (lotacao_atual.uorg_id if lotacao_atual else None),
                "uorg_id": grade_atual.uorg_id if grade_atual else (lotacao_atual.uorg_id if lotacao_atual else None),
                "posto_id": resolved_posto_id,
                "escala_padrao": func_obj.escala.sigla if func_obj.escala else "-",
                "escala_codigo": func_obj.escala.codigo if (func_obj.escala and func_obj.escala.codigo) else (func_obj.escala.sigla if func_obj.escala else "-"),
                "posto_nome": posto_nome,
                "carga_horaria_total": carga_horaria_semanal,
                "carga_horaria_semanal": carga_horaria_semanal,
                "carga_horaria_mensal_teto": carga_horaria_mensal_teto,
                "total_horas_escaladas": total_horas_escaladas,
                "total_horas_unidade": total_horas_unidade,
                "horas_excedentes": horas_excedentes,
                "saldo_horas": saldo_ch,
                "ultrapassou_carga_horaria": ultrapassou_ch,
                "has_multiple_lotacoes": has_multiple_lotacoes,
                "total_lotacoes": len(lotacoes_ativas),
                "lotacoes_info": lotacoes_info,
                "is_ferias_mes": len(ferias_no_mes) > 0,
                "is_diarista": is_diarista,
                "grade_id": grade_atual.id if grade_atual else None,
                "grade_status": status_atual,
                "is_bloqueada": (status_atual == "Publicada"),
                "observacao": grade_atual.observacao if grade_atual else None,
                "dias": dias_list
            })
        # Ordenação padrão da matriz:
        # 1º: Quem possui dados de escala / plantões preenchidos no mês (1 vem antes de 0)
        # 2º: Cargo alfabético
        # 3º: Nome do colaborador dentro do cargo
        def _has_dados(item):
            if item.get("grade_id") and item.get("total_horas_escaladas", 0) > 0:
                return 1
            dias = item.get("dias") or []
            return 1 if any(d.get("sigla") or d.get("is_ferias") or d.get("is_outra_unidade") for d in dias) else 0

        matrix_items.sort(
            key=lambda x: (
                - _has_dados(x),
                (x.get("cargo") or "").lower(),
                (x.get("nome") or "").lower()
            )
        )

        return matrix_items

    @staticmethod
    async def enviar_superior(session: AsyncSession, id: int, login: str, observacao: Optional[str] = None) -> Optional[Grade]:
        """
        Encaminha/libera a grade para o superior imediato (UORG Pai).
        """
        grade = await GradeProvider.get_by_id(session, id)
        if not grade:
            return None
        grade.status = "Enviada_Superior"
        grade.login = login
        if observacao:
            grade.observacao = observacao
        await session.commit()
        return await GradeProvider.get_by_id(session, id)

    @staticmethod
    async def enviar_lote_superior(
        session: AsyncSession,
        unidade_id: int,
        mes: int,
        ano: int,
        login: str
    ) -> int:
        """
        Encaminha em lote todas as grades de uma UORG para a chefia superior imediata.
        """
        stmt = (
            update(Grade)
            .where(
                and_(
                    Grade.uorg_id == unidade_id,
                    Grade.mes == mes,
                    Grade.ano == ano,
                    Grade.status != "Publicada"
                )
            )
            .values(status="Enviada_Superior", login=login)
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount

    @staticmethod
    async def devolver_grade(session: AsyncSession, id: int, login: str, motivo: Optional[str] = None) -> Optional[Grade]:
        """
        Devolve a grade encaminhada para ajustes pela chefia local.
        """
        grade = await GradeProvider.get_by_id(session, id)
        if not grade:
            return None
        grade.status = "Devolvida"
        grade.login = login
        if motivo:
            grade.observacao = f"Devolvida por {login}: {motivo}"
        await session.commit()
        return await GradeProvider.get_by_id(session, id)

    @staticmethod
    async def publish_grade(session: AsyncSession, id: int, login: str) -> Optional[Grade]:
        """
        Publica uma grade individual, tornando-a visível para a DIVGP.
        """
        grade = await GradeProvider.get_by_id(session, id)
        if not grade:
            return None
        grade.status = "Publicada"
        grade.login = login
        await session.commit()
        return await GradeProvider.get_by_id(session, id)

    @staticmethod
    async def publish_all_in_unit(
        session: AsyncSession,
        unidade_id: int,
        mes: int,
        ano: int,
        login: str
    ) -> int:
        """
        Publica todas as grades de uma unidade no mês/ano de referência em lote para a DIVGP.
        """
        stmt = (
            update(Grade)
            .where(
                and_(
                    Grade.uorg_id == unidade_id,
                    Grade.mes == mes,
                    Grade.ano == ano
                )
            )
            .values(status="Publicada", login=login)
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount

    @staticmethod
    async def get_indicators(
        session: AsyncSession,
        unidade_id: Optional[int],
        mes: int,
        ano: int,
        posto_id: Optional[int] = None,
        cargo_id: Optional[int] = None,
        search_term: Optional[str] = None,
        incluir_subordinadas: bool = True
    ) -> Dict[str, int]:
        """
        Calcula os 3 indicadores de gestão da unidade para o mês de referência:
        1. Total de colaboradores no setor/unidade (respeitando filtros de posto, cargo e busca)
        2. Colaboradores de férias no mês
        3. Colaboradores com múltiplas lotações
        """
        _, last_day = calendar.monthrange(ano, mes)
        start_of_month = date(ano, mes, 1)
        end_of_month = date(ano, mes, last_day)

        target_uorg_ids = []
        if unidade_id:
            if incluir_subordinadas:
                from src.providers.uorg_provider import UorgProvider
                target_uorg_ids = await UorgProvider.get_descendant_ids(session, unidade_id)
            else:
                target_uorg_ids = [unidade_id]

        # 1. Obter colaboradores ativos na unidade
        lotacao_filters = [
            FuncionarioLotacao.data_inicio <= end_of_month,
            or_(
                FuncionarioLotacao.data_fim.is_(None),
                FuncionarioLotacao.data_fim >= start_of_month
            )
        ]
        if target_uorg_ids:
            lotacao_filters.append(FuncionarioLotacao.uorg_id.in_(target_uorg_ids))
        if posto_id:
            lotacao_filters.append(FuncionarioLotacao.posto_id == posto_id)

        stmt_lotacoes = (
            select(FuncionarioLotacao.funcionario_id)
            .where(and_(*lotacao_filters))
            .distinct()
        )
        result_lotacoes = await session.execute(stmt_lotacoes)
        lot_ids = set(result_lotacoes.scalars().all())

        grade_filters = [
            Grade.mes == mes,
            Grade.ano == ano
        ]
        if target_uorg_ids:
            grade_filters.append(Grade.uorg_id.in_(target_uorg_ids))
        if posto_id:
            grade_filters.append(Grade.posto_id == posto_id)

        if target_uorg_ids or posto_id:
            stmt_grades_func = (
                select(Grade.funcionario_id)
                .where(and_(*grade_filters))
                .distinct()
            )
            result_grades_func = await session.execute(stmt_grades_func)
            grade_func_ids = set(result_grades_func.scalars().all())
            func_ids = list(lot_ids.union(grade_func_ids))
        else:
            func_ids = list(lot_ids)

        if not func_ids:
            return {
                "total_colaboradores": 0,
                "total_ferias": 0,
                "total_multiplas_lotacoes": 0
            }

        # Aplicar filtros de cargo e busca textual se fornecidos
        if cargo_id or search_term:
            func_conds = [Funcionario.id.in_(func_ids)]
            if cargo_id:
                func_conds.append(Funcionario.cargo_id == cargo_id)
            if search_term:
                term = f"%{search_term.strip()}%"
                func_conds.append(
                    or_(
                        Funcionario.nome.ilike(term),
                        Funcionario.matricula.ilike(term)
                    )
                )
            stmt_filter_funcs = select(Funcionario.id).where(and_(*func_conds))
            res_filter = await session.execute(stmt_filter_funcs)
            func_ids = list(res_filter.scalars().all())

        if not func_ids:
            return {
                "total_colaboradores": 0,
                "total_ferias": 0,
                "total_multiplas_lotacoes": 0
            }

        total_colaboradores = len(func_ids)

        # 2. Total de colaboradores de férias no mês
        stmt_ferias = (
            select(FuncionarioFerias.funcionario_id)
            .where(
                and_(
                    FuncionarioFerias.funcionario_id.in_(func_ids),
                    FuncionarioFerias.data_inicio <= end_of_month,
                    FuncionarioFerias.data_fim >= start_of_month
                )
            )
            .distinct()
        )
        result_ferias = await session.execute(stmt_ferias)
        total_ferias = len(result_ferias.scalars().all())

        # 3. Total de colaboradores com múltiplas lotações ativas
        stmt_multiplas = (
            select(FuncionarioLotacao.funcionario_id)
            .where(
                and_(
                    FuncionarioLotacao.funcionario_id.in_(func_ids),
                    FuncionarioLotacao.data_inicio <= end_of_month,
                    or_(
                        FuncionarioLotacao.data_fim.is_(None),
                        FuncionarioLotacao.data_fim >= start_of_month
                    )
                )
            )
            .group_by(FuncionarioLotacao.funcionario_id)
            .having(func.count(FuncionarioLotacao.id) > 1)
        )
        result_multiplas = await session.execute(stmt_multiplas)
        total_multiplas = len(result_multiplas.scalars().all())

        return {
            "total_colaboradores": total_colaboradores,
            "total_ferias": total_ferias,
            "total_multiplas_lotacoes": total_multiplas
        }

    @staticmethod
    async def create(
        session: AsyncSession,
        grade_data: dict,
        dias_data: List[dict],
        login: str
    ) -> Grade:
        grade_data["login"] = login
        if "unidade_id" in grade_data and "uorg_id" not in grade_data:
            grade_data["uorg_id"] = grade_data.pop("unidade_id")
        nova_grade = Grade(**grade_data)
        for d in dias_data:
            nova_grade.dias.append(GradeDia(
                dia=d["dia"],
                escala_id=d.get("escala_id"),
                legenda_sigla=d.get("legenda_sigla"),
                descricao=d.get("descricao")
            ))
        session.add(nova_grade)
        await session.commit()
        return await GradeProvider.get_by_id(session, nova_grade.id)

    @staticmethod
    async def update(
        session: AsyncSession,
        id: int,
        grade_data: dict,
        dias_data: Optional[List[dict]],
        login: str
    ) -> Optional[Grade]:
        grade = await GradeProvider.get_by_id(session, id)
        if not grade:
            return None

        grade.login = login
        if "unidade_id" in grade_data and "uorg_id" not in grade_data:
            grade_data["uorg_id"] = grade_data.pop("unidade_id")
        for key, value in grade_data.items():
            if hasattr(grade, key):
                setattr(grade, key, value)

        if dias_data is not None:
            await session.execute(delete(GradeDia).where(GradeDia.grade_id == id))
            await session.flush()
            session.expire(grade, ["dias"])

            for d in dias_data:
                d_item = GradeDia(
                    grade_id=id,
                    dia=d["dia"],
                    escala_id=d.get("escala_id"),
                    legenda_sigla=d.get("legenda_sigla"),
                    descricao=d.get("descricao")
                )
                session.add(d_item)
            await session.flush()
            session.expire(grade, ["dias"])

        await session.commit()
        return await GradeProvider.get_by_id(session, id)

    @staticmethod
    async def delete(session: AsyncSession, id: int) -> bool:
        await session.execute(delete(GradeDia).where(GradeDia.grade_id == id))
        stmt = delete(Grade).where(Grade.id == id)
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0

    @staticmethod
    async def copy_grade(
        session: AsyncSession,
        source_func_id: Optional[int],
        source_unidade_id: int,
        source_mes: int,
        source_ano: int,
        target_func_ids: List[int],
        target_unidade_id: int,
        target_mes: int,
        target_ano: int,
        login: str,
        source_func_ids: Optional[List[int]] = None,
        target_posto_id: Optional[int] = None
    ) -> List[Grade]:
        """
        Copia a grade de um colaborador de origem (ou múltiplos colaboradores de origem para si mesmos)
        mantendo o mesmo colaborador e mesmo posto de serviço.
        """
        _, target_last_day = calendar.monthrange(target_ano, target_mes)
        start_of_target_month = date(target_ano, target_mes, 1)
        end_of_target_month = date(target_ano, target_mes, target_last_day)

        # 1. Buscar feriados do mês de destino
        stmt_feriados = select(Feriado).where(
            and_(
                Feriado.data >= start_of_target_month,
                Feriado.data <= end_of_target_month
            )
        )
        res_feriados = await session.execute(stmt_feriados)
        feriados_alvo_dias = {f.data.day for f in res_feriados.scalars().all()}

        # 2. Buscar férias cadastradas no mês de destino para os funcionários envolvidos
        todos_target_ids = list(set((source_func_ids or []) + target_func_ids))
        stmt_ferias = select(FuncionarioFerias).where(
            and_(
                FuncionarioFerias.funcionario_id.in_(todos_target_ids),
                FuncionarioFerias.data_inicio <= end_of_target_month,
                FuncionarioFerias.data_fim >= start_of_target_month
            )
        )
        res_ferias = await session.execute(stmt_ferias)
        ferias_por_func = {}
        for ff in res_ferias.scalars().all():
            if ff.funcionario_id not in ferias_por_func:
                ferias_por_func[ff.funcionario_id] = []
            ferias_por_func[ff.funcionario_id].append(ff)

        def is_afastamento_ou_ferias_ou_feriado(sigla: Optional[str], descricao: Optional[str]) -> bool:
            """Verifica se a sigla ou descrição representa férias, feriado ou afastamento"""
            if not sigla:
                return False
            s = sigla.strip().upper()
            d = (descricao or "").strip().upper()

            # Se for um turno válido de trabalho (diarista ou plantonista), NÃO bloqueia a cópia mesmo se a descrição citar feriado
            if (
                (s in GradeProvider.TURNOS_DIARISTA_MAP or s in GradeProvider.TURNOS_PLANTONISTA_MAP)
                and s not in ["FD", "FD6", "FD8", "FR", "FER", "FERIADO"]
                and not s.startswith("FE")
            ):
                return False

            # Férias
            if s in ["FE", "FERIAS"] or s.startswith("FE") or "FÉRIAS" in d or "FERIAS" in d:
                return True
            # Feriados
            if s in ["FR", "FD0", "FERIADO"] or "FERIADO" in d:
                return True
            # Afastamentos / Licenças
            if s in ["LM", "LP", "A", "FJ", "LIC", "LMS", "LMT", "AF", "AFASTAMENTO"] or "LICENÇA" in d or "LICENCA" in d or "AFASTAMENTO" in d:
                return True
            # Abonos
            if s.startswith("AB"):
                return True
            return False

        created_or_updated_grades = []

        # Cenário 1: Cópia de múltiplos colaboradores de origem para si mesmos no mês/ano destino
        # Se source_func_ids for fornecido, a cópia é 1-para-1 (cada funcionário da origem para o mesmo funcionário no destino)
        if source_func_ids and len(source_func_ids) > 0:
            funcs_to_copy = [fid for fid in source_func_ids if fid in target_func_ids]
            if not funcs_to_copy:
                funcs_to_copy = target_func_ids

            for f_id in funcs_to_copy:
                src_grade = await GradeProvider.get_by_funcionario_unidade_mes_ano(
                    session, f_id, source_unidade_id, source_mes, source_ano
                )
                if not src_grade:
                    continue

                existing_grade = await GradeProvider.get_by_funcionario_unidade_mes_ano(
                    session, f_id, target_unidade_id, target_mes, target_ano
                )

                func_ferias_list = ferias_por_func.get(f_id, [])

                source_dias = {d.dia: d for d in src_grade.dias}
                dias_para_inserir = []
                for dia_num in range(1, target_last_day + 1):
                    dia_date = date(target_ano, target_mes, dia_num)

                    # Se o dia no mês destino for feriado, NÃO copia escala de trabalho para ele
                    if dia_num in feriados_alvo_dias:
                        continue

                    # Se o colaborador estiver de férias nesse dia no mês destino, NÃO copia
                    if any(ff.data_inicio <= dia_date <= ff.data_fim for ff in func_ferias_list):
                        continue

                    src_dia = source_dias.get(dia_num)
                    if src_dia:
                        # Se na origem o dia era férias, feriado ou afastamento, NÃO copia
                        if is_afastamento_ou_ferias_ou_feriado(src_dia.legenda_sigla, src_dia.descricao):
                            continue

                        dias_para_inserir.append({
                            "dia": dia_num,
                            "escala_id": src_dia.escala_id,
                            "legenda_sigla": src_dia.legenda_sigla,
                            "descricao": src_dia.descricao
                        })

                posto_final = target_posto_id or src_grade.posto_id

                if existing_grade:
                    updated = await GradeProvider.update(
                        session,
                        existing_grade.id,
                        {
                            "status": "Rascunho",
                            "posto_id": posto_final,
                            "observacao": f"Escala copiada de {source_mes}/{source_ano}"
                        },
                        dias_para_inserir,
                        login
                    )
                    created_or_updated_grades.append(updated)
                else:
                    created = await GradeProvider.create(
                        session,
                        {
                            "funcionario_id": f_id,
                            "unidade_id": target_unidade_id,
                            "posto_id": posto_final,
                            "mes": target_mes,
                            "ano": target_ano,
                            "status": "Rascunho",
                            "observacao": f"Escala copiada de {source_mes}/{source_ano}"
                        },
                        dias_para_inserir,
                        login
                    )
                    created_or_updated_grades.append(created)

            await session.commit()
            return created_or_updated_grades

        # Cenário 2: Cópia padrão de um colaborador de origem (source_func_id) para target_func_ids
        if not source_func_id:
            raise ValueError("Colaborador de origem não especificado.")

        source_grade = await GradeProvider.get_by_funcionario_unidade_mes_ano(
            session, source_func_id, source_unidade_id, source_mes, source_ano
        )
        if not source_grade:
            raise ValueError("Grade de origem não encontrada.")

        source_dias = {d.dia: d for d in source_grade.dias}

        for target_func_id in target_func_ids:
            existing_grade = await GradeProvider.get_by_funcionario_unidade_mes_ano(
                session, target_func_id, target_unidade_id, target_mes, target_ano
            )

            func_ferias_list = ferias_por_func.get(target_func_id, [])

            dias_para_inserir = []
            for dia_num in range(1, target_last_day + 1):
                dia_date = date(target_ano, target_mes, dia_num)

                # Se o dia no mês destino for feriado, NÃO copia
                if dia_num in feriados_alvo_dias:
                    continue

                # Se o colaborador estiver de férias nesse dia no mês destino, NÃO copia
                if any(ff.data_inicio <= dia_date <= ff.data_fim for ff in func_ferias_list):
                    continue

                src_dia = source_dias.get(dia_num)
                if src_dia:
                    # Se na origem o dia era férias, feriado ou afastamento, NÃO copia
                    if is_afastamento_ou_ferias_ou_feriado(src_dia.legenda_sigla, src_dia.descricao):
                        continue

                    dias_para_inserir.append({
                        "dia": dia_num,
                        "escala_id": src_dia.escala_id,
                        "legenda_sigla": src_dia.legenda_sigla,
                        "descricao": src_dia.descricao
                    })

            posto_final = target_posto_id or source_grade.posto_id

            if existing_grade:
                updated = await GradeProvider.update(
                    session,
                    existing_grade.id,
                    {
                        "status": "Rascunho",
                        "posto_id": posto_final,
                        "observacao": f"Copiada de {source_grade.funcionario_id} ({source_mes}/{source_ano})"
                    },
                    dias_para_inserir,
                    login
                )
                created_or_updated_grades.append(updated)
            else:
                created = await GradeProvider.create(
                    session,
                    {
                        "funcionario_id": target_func_id,
                        "unidade_id": target_unidade_id,
                        "posto_id": posto_final,
                        "mes": target_mes,
                        "ano": target_ano,
                        "status": "Rascunho",
                        "observacao": f"Copiada de {source_grade.funcionario_id} ({source_mes}/{source_ano})"
                    },
                    dias_para_inserir,
                    login
                )
                created_or_updated_grades.append(created)

        await session.commit()
        return created_or_updated_grades
