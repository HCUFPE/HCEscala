from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from ..resources.database import get_app_db_session
from ..auth.auth import auth_handler
from ..routers.admin import verify_admin_group
from ..providers.audit_provider import AuditProvider

router = APIRouter(
    prefix="/api/audit-logs",
    tags=["Auditoria e Logs"],
    dependencies=[Depends(auth_handler.decode_token)]
)

class AuditLogResponse(BaseModel):
    id: int
    usuario: str
    tela: str
    tabela: str
    operacao: str
    registro_id: str
    dados_anteriores: Optional[str] = None
    dados_posteriores: Optional[str] = None
    data_hora: datetime
    revertido: bool
    revertido_por: Optional[str] = None
    revertido_em: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class PaginatedAuditLogsResponse(BaseModel):
    items: List[AuditLogResponse]
    total: int
    limit: int
    offset: int

class RevertResponse(BaseModel):
    sucesso: bool
    mensagem: str

@router.get("", response_model=PaginatedAuditLogsResponse)
async def list_audit_logs(
    tela: Optional[str] = None,
    usuario: Optional[str] = None,
    operacao: Optional[str] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_app_db_session),
    admin_user: dict = Depends(verify_admin_group)
):
    """
    Lista logs de auditoria com filtros avançados. Acesso restrito ao Administrador.
    """
    items, total = await AuditProvider.listar_logs(
        session=db,
        tela=tela,
        usuario=usuario,
        operacao=operacao,
        data_inicio=data_inicio,
        data_fim=data_fim,
        limit=limit,
        offset=offset
    )
    return PaginatedAuditLogsResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset
    )

@router.get("/telas", response_model=List[str])
async def list_audit_telas(
    db: AsyncSession = Depends(get_app_db_session),
    admin_user: dict = Depends(verify_admin_group)
):
    """
    Retorna a lista de telas que possuem registros de auditoria para o filtro select.
    """
    return await AuditProvider.obter_telas_unicas(db)

@router.get("/{id}", response_model=AuditLogResponse)
async def get_audit_log(
    id: int,
    db: AsyncSession = Depends(get_app_db_session),
    admin_user: dict = Depends(verify_admin_group)
):
    log = await AuditProvider.obter_por_id(db, id)
    if not log:
        raise HTTPException(status_code=404, detail="Log de auditoria não encontrado.")
    return log

@router.post("/{id}/revert", response_model=RevertResponse)
async def revert_audit_log(
    id: int,
    db: AsyncSession = Depends(get_app_db_session),
    admin_user: dict = Depends(verify_admin_group)
):
    """
    Reverte a operação do log de auditoria especificado. Acesso restrito ao Administrador.
    """
    admin_login = admin_user.get("username") or admin_user.get("sub") or "admin"
    res = await AuditProvider.reverter_log(db, id, admin_login)
    if not res["sucesso"]:
        raise HTTPException(status_code=400, detail=res["mensagem"])
    return RevertResponse(sucesso=True, mensagem=res["mensagem"])
