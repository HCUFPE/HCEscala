import json
from typing import List, Optional, Tuple, Any, Dict
from datetime import datetime
from sqlalchemy import select, desc, and_, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.audit_log import AuditLog
from src.helpers.audit_helper import registrar_log

# Mapeamento de tabelas para seus respectivos models SQLAlchemy
TABLE_MODEL_MAP = {
    "cargos": "src.models.cargo.Cargo",
    "escalas": "src.models.escala.Escala",
    "legendas": "src.models.legenda.Legenda",
    "feriados": "src.models.feriado.Feriado",
    "uorgs": "src.models.uorg.Uorg",
    "postos": "src.models.posto.Posto",
    "funcionarios": "src.models.funcionario.Funcionario",
    "funcionarios_lotacoes": "src.models.funcionario_lotacao.FuncionarioLotacao",
    "usuario_gerencias": "src.models.usuario_gerencia.UsuarioGerencia",
    "grades": "src.models.grade.Grade",
    "grade_dias": "src.models.grade.GradeDia",
}

class AuditProvider:
    @staticmethod
    async def listar_logs(
        session: AsyncSession,
        tela: Optional[str] = None,
        usuario: Optional[str] = None,
        operacao: Optional[str] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[AuditLog], int]:
        """
        Retorna a lista paginada e filtrada de logs de auditoria e o total de registros.
        """
        stmt = select(AuditLog)
        filters = []

        if tela:
            filters.append(AuditLog.tela.ilike(f"%{tela.strip()}%"))
        if usuario:
            filters.append(AuditLog.usuario.ilike(f"%{usuario.strip()}%"))
        if operacao and operacao.upper() != "TODAS":
            filters.append(AuditLog.operacao == operacao.upper())
        if data_inicio:
            filters.append(AuditLog.data_hora >= data_inicio)
        if data_fim:
            filters.append(AuditLog.data_hora <= data_fim)

        if filters:
            stmt = stmt.where(and_(*filters))

        # Obter contagem total
        count_stmt = select(AuditLog.id)
        if filters:
            count_stmt = count_stmt.where(and_(*filters))
        total_res = await session.execute(count_stmt)
        total = len(total_res.scalars().all())

        # Ordenar decrescente e paginar
        stmt = stmt.order_by(desc(AuditLog.data_hora)).limit(limit).offset(offset)
        result = await session.execute(stmt)
        logs = result.scalars().all()

        return logs, total

    @staticmethod
    async def obter_por_id(session: AsyncSession, log_id: int) -> Optional[AuditLog]:
        stmt = select(AuditLog).where(AuditLog.id == log_id)
        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    @staticmethod
    async def obter_telas_unicas(session: AsyncSession) -> List[str]:
        stmt = select(AuditLog.tela).distinct().order_by(AuditLog.tela)
        res = await session.execute(stmt)
        return [r for r in res.scalars().all() if r]

    @staticmethod
    async def reverter_log(session: AsyncSession, log_id: int, admin_login: str) -> Dict[str, Any]:
        """
        Reverte a alteracao registrada no log_id.
        """
        log = await AuditProvider.obter_por_id(session, log_id)
        if not log:
            return {"sucesso": False, "mensagem": "Log não encontrado."}
        if log.revertido:
            return {"sucesso": False, "mensagem": "Esta alteração já foi revertida anteriormente."}

        tabela = log.tabela.lower()
        operacao = log.operacao.upper()
        reg_id = log.registro_id

        dados_ant = json.loads(log.dados_anteriores) if log.dados_anteriores else None
        dados_pos = json.loads(log.dados_posteriores) if log.dados_posteriores else None

        try:
            # 1. Reverter UPDATE: restaurar dados_anteriores
            if operacao == "UPDATE":
                if not dados_ant:
                    return {"sucesso": False, "mensagem": "Não há dados anteriores para restaurar."}
                
                # Montar SET dinâmico com segurança baseado no dict
                set_clauses = []
                params = {"pk": int(reg_id) if reg_id.isdigit() else reg_id}
                for k, v in dados_ant.items():
                    if k in ["id", "data_alteracao", "updated_at", "created_at"]:
                        continue
                    set_clauses.append(f"{k} = :{k}")
                    params[k] = v
                
                if set_clauses:
                    sql = f"UPDATE {tabela} SET {', '.join(set_clauses)} WHERE id = :pk"
                    await session.execute(text(sql), params)

                # Registrar log de reversão
                await registrar_log(
                    session=session,
                    usuario=admin_login,
                    tela=log.tela,
                    tabela=log.tabela,
                    operacao="REVERT",
                    registro_id=reg_id,
                    dados_anteriores=dados_pos,
                    dados_posteriores=dados_ant
                )

            # 2. Reverter INSERT: deletar o registro criado
            elif operacao == "INSERT":
                params = {"pk": int(reg_id) if reg_id.isdigit() else reg_id}
                sql = f"DELETE FROM {tabela} WHERE id = :pk"
                await session.execute(text(sql), params)

                # Registrar log de reversão
                await registrar_log(
                    session=session,
                    usuario=admin_login,
                    tela=log.tela,
                    tabela=log.tabela,
                    operacao="REVERT",
                    registro_id=reg_id,
                    dados_anteriores=dados_pos,
                    dados_posteriores=None
                )

            # 3. Reverter DELETE: recriar o registro com dados_anteriores
            elif operacao == "DELETE":
                if not dados_ant:
                    return {"sucesso": False, "mensagem": "Não há dados anteriores para recriar o registro."}

                cols = []
                placeholders = []
                params = {}
                for k, v in dados_ant.items():
                    cols.append(k)
                    placeholders.append(f":{k}")
                    params[k] = v

                sql = f"INSERT INTO {tabela} ({', '.join(cols)}) VALUES ({', '.join(placeholders)})"
                await session.execute(text(sql), params)

                # Registrar log de reversão
                await registrar_log(
                    session=session,
                    usuario=admin_login,
                    tela=log.tela,
                    tabela=log.tabela,
                    operacao="REVERT",
                    registro_id=reg_id,
                    dados_anteriores=None,
                    dados_posteriores=dados_ant
                )
            else:
                return {"sucesso": False, "mensagem": f"Operação '{operacao}' não suporta reversão direta."}

            # Marcar o log como revertido
            log.revertido = True
            log.revertido_por = admin_login
            log.revertido_em = datetime.now()

            await session.commit()
            return {"sucesso": True, "mensagem": f"Alteração ID {log_id} revertida com sucesso!"}

        except Exception as e:
            await session.rollback()
            return {"sucesso": False, "mensagem": f"Falha ao reverter: {str(e)}"}
