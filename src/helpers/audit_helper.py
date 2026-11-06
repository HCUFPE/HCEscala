"""
Helper Utilitário de Registro de Auditoria e Trilha de Mudanças
================================================================
Funções padronizadas para registrar logs de auditoria em rotas, providers e controllers.
"""

import json
import logging
from datetime import datetime, date
from typing import Optional, Any, Dict
from sqlalchemy.inspection import inspect
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.audit_log import AuditLog

logger = logging.getLogger("audit")


def model_to_dict(obj: Any) -> Optional[Dict[str, Any]]:
    """
    Converte uma instância de modelo SQLAlchemy em um dicionário serializável em JSON.
    """
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj
    try:
        mapper = inspect(obj.__class__)
        data: Dict[str, Any] = {}
        for column in mapper.columns:
            val = getattr(obj, column.key, None)
            if isinstance(val, (datetime, date)):
                data[column.key] = val.isoformat()
            else:
                data[column.key] = val
        return data
    except Exception:
        return {
            k: (v.isoformat() if isinstance(v, (datetime, date)) else v)
            for k, v in getattr(obj, "__dict__", {}).items()
            if not k.startswith("_")
        }


async def registrar_log(
    session: AsyncSession,
    usuario: str,
    tela: str,
    tabela: str,
    operacao: str,
    registro_id: Any,
    dados_anteriores: Optional[Any] = None,
    dados_posteriores: Optional[Any] = None
) -> Optional[AuditLog]:
    """
    Registra um evento de auditoria na tabela audit_logs dentro da transação atual.
    """
    try:
        if isinstance(dados_anteriores, str) or dados_anteriores is None:
            str_anteriores = dados_anteriores
        else:
            str_anteriores = json.dumps(dados_anteriores, ensure_ascii=False, default=str)

        if isinstance(dados_posteriores, str) or dados_posteriores is None:
            str_posteriores = dados_posteriores
        else:
            str_posteriores = json.dumps(dados_posteriores, ensure_ascii=False, default=str)

        log_entry = AuditLog(
            usuario=str(usuario or "sistema"),
            tela=str(tela or "Sistema"),
            tabela=str(tabela or "desconhecida"),
            operacao=str(operacao or "UPDATE").upper(),
            registro_id=str(registro_id if registro_id is not None else "0"),
            dados_anteriores=str_anteriores,
            dados_posteriores=str_posteriores,
            data_hora=datetime.now(),
            revertido=False
        )
        session.add(log_entry)
        await session.flush()
        return log_entry
    except Exception as e:
        logger.error(f"Erro ao registrar log de auditoria: {e}")
        return None


async def registrar_auditoria(
    db: AsyncSession,
    usuario: str,
    categoria: str,
    acao: str,
    recurso: str,
    dados_anteriores: Optional[Any] = None,
    dados_novos: Optional[Any] = None,
    ip_origem: Optional[str] = None
) -> Optional[AuditLog]:
    """
    Alias compatível com o padrão SETISD para registrar eventos de auditoria.
    """
    partes = str(recurso or "sistema:0").split(":", 1)
    tabela = partes[0]
    registro_id = partes[1] if len(partes) > 1 else "0"
    log_entry = await registrar_log(
        session=db,
        usuario=usuario,
        tela=categoria,
        tabela=tabela,
        operacao=acao,
        registro_id=registro_id,
        dados_anteriores=dados_anteriores,
        dados_posteriores=dados_novos
    )
    if log_entry is not None:
        await db.commit()
    return log_entry
