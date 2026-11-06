from typing import Optional, List, Dict, Any
import calendar
from datetime import date
from fastapi import HTTPException
from sqlalchemy import select, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.providers.grade_provider import GradeProvider
from src.providers.funcionario_provider import FuncionarioProvider
from src.providers.gerencia_provider import GerenciaProvider
from src.models.grade import Grade
from src.models.feriado import Feriado
from src.models.escala import Escala

import unicodedata

def _normalize_text(text: str) -> str:
    if not text:
        return ""
    nfkd = unicodedata.normalize('NFKD', text)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).upper().strip()

def _is_cargo_medico(nome: str) -> bool:
    norm = _normalize_text(nome)
    return "MEDICO" in norm

def _is_cargo_assistencial(nome: str) -> bool:
    norm = _normalize_text(nome)
    # Lista abrangente normalizada sem acentos
    assistenciais = [
        "ENFERMEIR",
        "TEC. ENFERMAGEM",
        "TEC ENFERMAGEM",
        "TEC. DE ENFERMAGEM",
        "TEC DE ENFERMAGEM",
        "TEC. EM ENFERMAGEM",
        "TEC EM ENFERMAGEM",
        "TECNICO EM ENFERMAGEM",
        "TECNICO DE ENFERMAGEM",
        "TECNICO ENFERMAGEM",
        "AUXILIAR DE ENFERMAGEM",
        "AUXILIAR EM ENFERMAGEM",
        "AUXILIAR ENFERMAGEM",
        "ENFERMAGEM",
        "FISIOTERAP",
        "MEDICO",
        "ODONTOLOG",
        "DENTISTA",
        "PSICOLOG",
        "NUTRICION",
        "FONOAUDIOLOG",
        "TERAPEUTA OCUPACIONAL",
        "ASSISTENTE SOCIAL",
        "BIOMEDIC",
        "FARMACEUTIC",
        "BIOLOGO",
        "TERAPIA OCUPACIONAL",
        "TECNICO EM RADIOLOGIA",
        "TECNICO DE RADIOLOGIA",
        "RADIOLOGIA",
        "TECNICO EM NUTRICAO",
        "TECNICO DE NUTRICAO",
        "TECNICO EM FARMACIA",
        "TECNICO DE FARMACIA",
        "TECNICO EM ANALISES CLINICAS",
        "TECNICO DE ANALISES CLINICAS",
        "TECNICO EM LABORATORIO",
        "TECNICO DE LABORATORIO"
    ]
    return any(a in norm for a in assistenciais)

class GradeController:
    @staticmethod
    async def _validar_regras_escala(
        session: AsyncSession,
        funcionario_id: int,
        dias: Optional[List[dict]]
    ):
        if not dias:
            return

        func = await FuncionarioProvider.get_by_id(session, funcionario_id)
        if not func or not func.cargo:
            return

        cargo_nome = func.cargo.nome
        is_medico = _is_cargo_medico(cargo_nome)
        is_assistencial = _is_cargo_assistencial(cargo_nome)

        # Buscar todas as escalas utilizadas nos dias informados
        siglas = [d.get("legenda_sigla") for d in dias if d.get("legenda_sigla")]
        if not siglas:
            return

        stmt = select(Escala).where(Escala.sigla.in_(siglas))
        res = await session.execute(stmt)
        escalas = {e.sigla: e for e in res.scalars().all()}

        for dia in dias:
            sigla = dia.get("legenda_sigla")
            if not sigla:
                continue
            
            escala = escalas.get(sigla)
            if not escala:
                continue

            # Regras de Negócio
            sigla_lower = escala.sigla.lower()
            
            if sigla_lower.startswith("dn"):
                if not is_medico:
                    raise HTTPException(
                        status_code=400,
                        detail=f"A escala '{escala.sigla}' (Plantão) é permitida apenas para médicos. Cargo atual: {cargo_nome}."
                    )
            elif sigla_lower.startswith("d") or sigla_lower.startswith("n"):
                if not is_assistencial:
                    raise HTTPException(
                        status_code=400,
                        detail=f"A escala '{escala.sigla}' (12x36) é permitida apenas para profissionais assistenciais. Cargo atual: {cargo_nome}."
                    )

    @staticmethod
    async def _validar_carga_horaria(
        session: AsyncSession,
        funcionario_id: int,
        unidade_id: int,
        mes: int,
        ano: int,
        dias: Optional[List[dict]],
        permitir_excedente: bool = False
    ):
        if dias is None or len(dias) == 0:
            return

        func = await FuncionarioProvider.get_by_id(session, funcionario_id)
        if not func:
            return

        carga_semanal = getattr(func, "carga_horaria", None) or 40
        _, last_day = calendar.monthrange(ano, mes)

        # Feriados no mês
        stmt_feriados = select(Feriado).where(
            and_(
                extract('year', Feriado.data) == ano,
                extract('month', Feriado.data) == mes
            )
        )
        res_fer = await session.execute(stmt_feriados)
        feriados_dias = set(f.data.day for f in res_fer.scalars().all())

        escala_sigla = func.escala.sigla.upper() if func.escala and func.escala.sigla else ""
        escala_codigo = func.escala.codigo.upper() if func.escala and func.escala.codigo else ""
        is_diarista = (
            (func.escala and not func.escala.apenas_assistenciais)
            or any(term in escala_sigla for term in ["DIARISTA", "5X2", "ADM", "SEG-SEX", "40H", "30H", "20H"])
            or ("DIARISTA" in escala_codigo)
        )

        # Calcular horas em outras unidades do colaborador no mesmo mês/ano
        stmt_outras = select(Grade).options(selectinload(Grade.dias)).where(
            and_(
                Grade.funcionario_id == funcionario_id,
                Grade.uorg_id != unidade_id,
                Grade.mes == mes,
                Grade.ano == ano
            )
        )
        res_outras = await session.execute(stmt_outras)
        outras_grades = res_outras.scalars().all()

        todas_siglas = [d.get("legenda_sigla") for d in dias if d.get("legenda_sigla")]
        for og in outras_grades:
            todas_siglas.extend([od.legenda_sigla for od in og.dias if od.legenda_sigla])

        horas_diarista = GradeProvider.obter_horas_diarista_colaborador(
            todas_siglas, escala_sigla, carga_semanal
        )
        if horas_diarista > 0:
            is_diarista = True
        elif any((s or "").strip().upper() in GradeProvider.TURNOS_PLANTONISTA_MAP for s in todas_siglas):
            is_diarista = False
        elif is_diarista:
            horas_diarista = round(carga_semanal / 5.0, 1)

        # Calcular horas na grade sendo salva/alterada e nos dias úteis trabalhados
        horas_por_dia = {}
        horas_grade = 0.0
        for d in dias:
            sig = d.get("legenda_sigla")
            if sig:
                dia_num = int(d.get("dia", 0))
                is_dia_util_semana = (1 <= dia_num <= last_day and date(ano, mes, dia_num).weekday() < 5)
                horas_ferias_dia = (
                    (horas_diarista if horas_diarista > 0 else round(carga_semanal / 5.0, 1))
                    if is_dia_util_semana
                    else 0.0
                )
                h = GradeProvider.calcular_horas_turno(
                    sig,
                    horas_diarista=horas_diarista,
                    horas_ferias_dia=horas_ferias_dia,
                    is_dia_util_semana=is_dia_util_semana
                )
                horas_grade += h
                if dia_num:
                    horas_por_dia[dia_num] = horas_por_dia.get(dia_num, 0.0) + h

        horas_outras = 0.0
        for og in outras_grades:
            for od in og.dias:
                if od.legenda_sigla:
                    is_dia_util_semana = (1 <= od.dia <= last_day and date(ano, mes, od.dia).weekday() < 5)
                    horas_ferias_dia = (
                        (horas_diarista if horas_diarista > 0 else round(carga_semanal / 5.0, 1))
                        if is_dia_util_semana
                        else 0.0
                    )
                    h = GradeProvider.calcular_horas_turno(
                        od.legenda_sigla,
                        horas_diarista=horas_diarista,
                        horas_ferias_dia=horas_ferias_dia,
                        is_dia_util_semana=is_dia_util_semana
                    )
                    horas_outras += h
                    horas_por_dia[od.dia] = horas_por_dia.get(od.dia, 0.0) + h

        dias_uteis = sum(
            1
            for d_num in range(1, last_day + 1)
            if date(ano, mes, d_num).weekday() < 5
            and (is_diarista or d_num not in feriados_dias or horas_por_dia.get(d_num, 0.0) > 0)
        )
        teto_mensal = GradeProvider.calcular_teto_mensal(carga_semanal, last_day, dias_uteis, is_diarista)

        total_acumulado = round(horas_grade + horas_outras, 1)

        if total_acumulado > teto_mensal and not permitir_excedente:
            excedente = round(total_acumulado - teto_mensal, 1)
            raise HTTPException(
                status_code=400,
                detail=f"A escala totaliza {total_acumulado:.0f}h e ultrapassa a carga horária mensal máxima permitida de {teto_mensal:.0f}h do colaborador {func.nome} ({func.cargo.nome}, {carga_semanal}h/sem). Excedente: +{excedente:.0f}h."
            )

    @staticmethod
    async def get_matrix(
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
        if mes < 1 or mes > 12:
            raise HTTPException(status_code=400, detail="Mês inválido. O mês deve estar entre 1 e 12.")
        if ano < 2000 or ano > 2100:
            raise HTTPException(status_code=400, detail="Ano inválido.")

        return await GradeProvider.get_matrix_data(
            session=session,
            unidade_id=unidade_id,
            mes=mes,
            ano=ano,
            cargo_id=cargo_id,
            search_term=search_term,
            status_filter=status_filter,
            apenas_publicadas=apenas_publicadas,
            posto_id=posto_id,
            incluir_subordinadas=incluir_subordinadas
        )

    @staticmethod
    async def enviar_superior(session: AsyncSession, id: int, username: str, observacao: Optional[str] = None):
        """
        Libera/encaminha a escala individual para o superior imediato (UORG Pai).
        """
        grade = await GradeProvider.get_by_id(session, id)
        if not grade:
            raise HTTPException(status_code=404, detail="Grade não encontrada.")

        if grade.status == "Publicada":
            raise HTTPException(status_code=400, detail="Esta grade já foi homologada e publicada pela DIVGP.")

        # Validar carga horária antes de liberar para o superior
        dias_dict = [{"dia": d.dia, "legenda_sigla": d.legenda_sigla} for d in grade.dias]
        await GradeController._validar_carga_horaria(
            session=session,
            funcionario_id=grade.funcionario_id,
            unidade_id=grade.uorg_id,
            mes=grade.mes,
            ano=grade.ano,
            dias=dias_dict,
            permitir_excedente=False
        )

        return await GradeProvider.enviar_superior(session, id, username, observacao)

    @staticmethod
    async def enviar_lote_superior(session: AsyncSession, unidade_id: int, mes: int, ano: int, username: str):
        """
        Libera/encaminha em lote todas as escalas de uma UORG para a chefia superior imediata.
        """
        if mes < 1 or mes > 12 or ano < 2000 or ano > 2100:
            raise HTTPException(status_code=400, detail="Mês ou ano inválido.")
        total = await GradeProvider.enviar_lote_superior(session, unidade_id, mes, ano, username)
        return {"message": f"{total} escala(s) liberada(s) para a chefia superior imediata com sucesso.", "total": total}

    @staticmethod
    async def devolver_grade(session: AsyncSession, id: int, username: str, motivo: Optional[str] = None, user_groups: List[str] = None):
        """
        Devolve a escala para o gestor subordinado realizar correções.
        """
        grade = await GradeProvider.get_by_id(session, id)
        if not grade:
            raise HTTPException(status_code=404, detail="Grade não encontrada.")

        # Apenas gestores do nível superior (ou DIVGP) podem devolver
        is_top = await GerenciaProvider.is_top_level_manager(session, username, grade.uorg_id, user_groups)
        if not is_top:
            raise HTTPException(
                status_code=403,
                detail="Apenas o gestor de nível hierárquico superior pode devolver a escala para correções."
            )

        return await GradeProvider.devolver_grade(session, id, username, motivo)

    @staticmethod
    async def publish_grade(session: AsyncSession, id: int, username: str, user_groups: List[str] = None, is_admin: bool = False):
        grade = await GradeProvider.get_by_id(session, id)
        if not grade:
            raise HTTPException(status_code=404, detail="Grade não encontrada.")

        # Validar se o usuário é gestor do nível hierárquico mais alto
        is_top = await GerenciaProvider.is_top_level_manager(session, username, grade.uorg_id, user_groups)
        if not is_top and not is_admin:
            raise HTTPException(
                status_code=403,
                detail="Apenas o gerente do nível hierárquico mais alto (ou a DIVGP) pode homologar e liberar a escala para publicação. Utilize a opção 'Liberar para Superior'."
            )
        
        # Validar carga horária antes de publicar
        dias_dict = [{"dia": d.dia, "legenda_sigla": d.legenda_sigla} for d in grade.dias]
        await GradeController._validar_carga_horaria(
            session=session,
            funcionario_id=grade.funcionario_id,
            unidade_id=grade.uorg_id,
            mes=grade.mes,
            ano=grade.ano,
            dias=dias_dict,
            permitir_excedente=False
        )

        grade = await GradeProvider.publish_grade(session, id, username)
        return grade

    @staticmethod
    async def publish_all_in_unit(session: AsyncSession, unidade_id: int, mes: int, ano: int, username: str, user_groups: List[str] = None, is_admin: bool = False):
        if mes < 1 or mes > 12 or ano < 2000 or ano > 2100:
            raise HTTPException(status_code=400, detail="Mês ou ano inválido.")

        # Validar se o usuário é gestor do nível hierárquico mais alto
        is_top = await GerenciaProvider.is_top_level_manager(session, username, unidade_id, user_groups)
        if not is_top and not is_admin:
            raise HTTPException(
                status_code=403,
                detail="Apenas o gerente do nível hierárquico mais alto (ou a DIVGP) pode homologar e publicar todas as escalas para a DIVGP. Utilize a opção 'Liberar Todas para Superior'."
            )

        total = await GradeProvider.publish_all_in_unit(session, unidade_id, mes, ano, username)
        return {"message": f"{total} escala(s) publicada(s) com sucesso para a DIVGP.", "total": total}

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
        if mes < 1 or mes > 12:
            raise HTTPException(status_code=400, detail="Mês inválido. O mês deve estar entre 1 e 12.")
        if ano < 2000 or ano > 2100:
            raise HTTPException(status_code=400, detail="Ano inválido.")

        return await GradeProvider.get_indicators(
            session=session,
            unidade_id=unidade_id,
            mes=mes,
            ano=ano,
            posto_id=posto_id,
            cargo_id=cargo_id,
            search_term=search_term,
            incluir_subordinadas=incluir_subordinadas
        )

    @staticmethod
    async def get_by_id(session: AsyncSession, id: int):
        grade = await GradeProvider.get_by_id(session, id)
        if not grade:
            raise HTTPException(status_code=404, detail="Grade não encontrada.")
        return grade

    @staticmethod
    async def create(session: AsyncSession, data: dict, username: str, is_admin: bool = False):
        funcionario_id = data.get("funcionario_id")
        unidade_id = data.get("unidade_id")
        mes = data.get("mes")
        ano = data.get("ano")
        permitir_excedente = data.pop("permitir_excedente", False)

        if not funcionario_id or not unidade_id or not mes or not ano:
            raise HTTPException(
                status_code=400, 
                detail="Funcionário, Unidade, Mês e Ano são obrigatórios."
            )

        existente = await GradeProvider.get_by_funcionario_unidade_mes_ano(
            session, funcionario_id, unidade_id, mes, ano
        )
        if existente and existente.status == "Publicada" and not is_admin:
            raise HTTPException(
                status_code=403,
                detail="A grade deste colaborador já foi publicada para a DIVGP e está bloqueada para alterações pelo gerente. Contate a DIVGP ou o administrador."
            )

        dias = data.pop("dias", [])

        # Validação de regras específicas de negócio por escala
        await GradeController._validar_regras_escala(
            session=session,
            funcionario_id=funcionario_id,
            dias=dias
        )

        # Validação da carga horária
        await GradeController._validar_carga_horaria(
            session=session,
            funcionario_id=funcionario_id,
            unidade_id=unidade_id,
            mes=mes,
            ano=ano,
            dias=dias,
            permitir_excedente=permitir_excedente or is_admin
        )

        if existente:
            return await GradeProvider.update(session, existente.id, data, dias, username)

        return await GradeProvider.create(session, data, dias, username)

    @staticmethod
    async def update(session: AsyncSession, id: int, data: dict, username: str, is_admin: bool = False):
        grade = await GradeProvider.get_by_id(session, id)
        if not grade:
            raise HTTPException(status_code=404, detail="Grade não encontrada.")

        if grade.status == "Publicada" and not is_admin:
            raise HTTPException(
                status_code=403,
                detail="A grade já foi publicada para a DIVGP e está bloqueada para alterações pelo gerente da área. Contate a DIVGP para solicitar reabertura."
            )

        permitir_excedente = data.pop("permitir_excedente", False)
        dias = data.pop("dias", None)

        if dias is not None:
            # Validação de regras específicas de negócio por escala
            await GradeController._validar_regras_escala(
                session=session,
                funcionario_id=grade.funcionario_id,
                dias=dias
            )

            # Validação da carga horária
            await GradeController._validar_carga_horaria(
                session=session,
                funcionario_id=grade.funcionario_id,
                unidade_id=grade.unidade_id,
                mes=grade.mes,
                ano=grade.ano,
                dias=dias,
                permitir_excedente=permitir_excedente or is_admin
            )

        atualizado = await GradeProvider.update(session, id, data, dias, username)
        return atualizado

    @staticmethod
    async def delete(session: AsyncSession, id: int, is_admin: bool = False):
        grade = await GradeProvider.get_by_id(session, id)
        if not grade:
            raise HTTPException(status_code=404, detail="Grade não encontrada.")

        if grade.status == "Publicada" and not is_admin:
            raise HTTPException(
                status_code=403,
                detail="A grade já foi publicada para a DIVGP. e não pode ser excluída pelo gerente da área."
            )

        sucesso = await GradeProvider.delete(session, id)
        if not sucesso:
            raise HTTPException(status_code=500, detail="Erro ao excluir a grade.")
        return {"message": "Grade excluída com sucesso."}

    @staticmethod
    async def copy_grade(session: AsyncSession, data: dict, username: str, is_admin: bool = False):
        source_func_id = data.get("source_func_id")
        source_func_ids = data.get("source_func_ids") or []
        source_unidade_id = data.get("source_unidade_id")
        source_mes = data.get("source_mes")
        source_ano = data.get("source_ano")
        target_func_ids = data.get("target_func_ids", [])
        target_unidade_id = data.get("target_unidade_id") or source_unidade_id
        target_posto_id = data.get("target_posto_id")
        target_mes = data.get("target_mes") or source_mes
        target_ano = data.get("target_ano") or source_ano

        if not source_unidade_id or not source_mes or not source_ano:
            raise HTTPException(
                status_code=400,
                detail="Dados de origem (Unidade, Mês, Ano) são obrigatórios."
            )

        if not source_func_id and not source_func_ids:
            raise HTTPException(
                status_code=400,
                detail="Selecione ao menos um colaborador de origem."
            )

        if not target_func_ids:
            raise HTTPException(
                status_code=400,
                detail="Selecione ao menos um colaborador de destino para copiar a grade."
            )

        # Se não for admin, verificar se algum colaborador de destino já possui grade publicada
        if not is_admin:
            for t_func_id in target_func_ids:
                t_existente = await GradeProvider.get_by_funcionario_unidade_mes_ano(
                    session, t_func_id, target_unidade_id, target_mes, target_ano
                )
                if t_existente and t_existente.status == "Publicada":
                    raise HTTPException(
                        status_code=403,
                        detail=f"O colaborador de destino (ID {t_func_id}) já possui grade 'Publicada' para a DIVGP. e está bloqueado para sobrescrita."
                    )

        try:
            return await GradeProvider.copy_grade(
                session=session,
                source_func_id=source_func_id,
                source_unidade_id=source_unidade_id,
                source_mes=source_mes,
                source_ano=source_ano,
                target_func_ids=target_func_ids,
                target_unidade_id=target_unidade_id,
                target_mes=target_mes,
                target_ano=target_ano,
                login=username,
                source_func_ids=source_func_ids,
                target_posto_id=target_posto_id
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def reabrir_grade(session: AsyncSession, id: int, username: str, is_admin: bool = False):
        if not is_admin:
            raise HTTPException(status_code=403, detail="Apenas a DIVGP. ou administradores podem reabrir uma grade já publicada.")
        grade = await GradeProvider.get_by_id(session, id)
        if not grade:
            raise HTTPException(status_code=404, detail="Grade não encontrada.")
        grade.status = "Rascunho"
        grade.login = username
        await session.commit()
        return await GradeProvider.get_by_id(session, id)
