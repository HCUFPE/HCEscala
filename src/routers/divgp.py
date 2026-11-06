from fastapi import APIRouter, Depends, Query, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import date

from src.resources.database import get_app_db_session
from src.auth.auth import auth_handler
from src.controllers.divgp_controller import DivgpController
from src.routers.gerencia import get_current_user_info

router = APIRouter(
    prefix="/api/divgp",
    tags=["Painel DIVGP"],
    dependencies=[Depends(auth_handler.decode_token)]
)

# Roteador legado para compatibilidade de chamadas /api/digp
digp_router = APIRouter(
    prefix="/api/digp",
    tags=["Painel DIVGP"],
    dependencies=[Depends(auth_handler.decode_token)]
)

class DivgpSumarioResponse(BaseModel):
    total_unidades: int
    unidades_100: int
    unidades_pendentes: int
    total_colaboradores: int
    total_publicadas: int
    percentual_geral: float

class DivgpUnidadeStatusItem(BaseModel):
    uorg_id: Optional[int] = None
    uorg_nome: Optional[str] = None
    uorg_pai_id: Optional[int] = None
    uorg_pai_nome: Optional[str] = None
    unidade_id: int
    unidade_nome: str
    setor_id: Optional[int] = None
    setor_nome: str
    total_colaboradores: int
    total_publicadas: int
    total_pendentes: int
    total_sem_grade: int
    percentual_conclusao: float
    status_homologacao: str

class DivgpStatusUnidadesResponse(BaseModel):
    mes: int
    ano: int
    sumario: DivgpSumarioResponse
    unidades: List[DivgpUnidadeStatusItem]

class DivgpFaltanteItem(BaseModel):
    funcionario_id: int
    matricula: str
    nome: str
    cargo: str
    escala_padrao: str
    unidade_nome: str
    posto_nome: str
    grade_id: Optional[int] = None
    grade_status: str

class DivgpEscalaDetalheItem(BaseModel):
    funcionario_id: int
    matricula: str
    nome: str
    cargo: str
    cargo_id: Optional[int] = None
    codigo_escala: str
    escala_padrao: str
    uorg_id: Optional[int] = None
    uorg_nome: str
    uorg_pai_id: Optional[int] = None
    uorg_pai_nome: str
    posto_id: Optional[int] = None
    posto_nome: str
    grade_id: Optional[int] = None
    grade_status: str
    observacao: Optional[str] = None
    login_responsavel: Optional[str] = None
    data_alteracao: Optional[str] = None
    carga_horaria_semanal: int = 40
    carga_horaria_mensal_teto: float = 160.0
    total_horas_escaladas: float = 0.0
    saldo_horas: float = 0.0
    is_diarista: bool = False

@router.get("/status-unidades", response_model=DivgpStatusUnidadesResponse)
@digp_router.get("/status-unidades", response_model=DivgpStatusUnidadesResponse)
async def get_status_unidades(
    mes: Optional[int] = Query(None),
    ano: Optional[int] = Query(None),
    session: AsyncSession = Depends(get_app_db_session),
    user_info: dict = Depends(get_current_user_info)
):
    current_date = date.today()
    mes_target = mes if mes is not None else current_date.month
    ano_target = ano if ano is not None else current_date.year

    return await DivgpController.get_status_unidades(session, mes_target, ano_target, user_info["is_admin"])

@router.get("/faltantes", response_model=List[DivgpFaltanteItem])
@digp_router.get("/faltantes", response_model=List[DivgpFaltanteItem])
async def get_faltantes(
    unidade_id: int = Query(...),
    mes: Optional[int] = Query(None),
    ano: Optional[int] = Query(None),
    session: AsyncSession = Depends(get_app_db_session),
    user_info: dict = Depends(get_current_user_info)
):
    current_date = date.today()
    mes_target = mes if mes is not None else current_date.month
    ano_target = ano if ano is not None else current_date.year

    return await DivgpController.get_faltantes(session, unidade_id, mes_target, ano_target, user_info["is_admin"])

@router.get("/todas-escalas", response_model=List[DivgpEscalaDetalheItem])
@digp_router.get("/todas-escalas", response_model=List[DivgpEscalaDetalheItem])
async def get_todas_escalas(
    mes: Optional[int] = Query(None),
    ano: Optional[int] = Query(None),
    uorg_id: Optional[int] = Query(None),
    uorg_pai_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    cargo_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_app_db_session),
    user_info: dict = Depends(get_current_user_info)
):
    """
    Retorna todas as escalas hospitalares com seus respectivos status para o painel institucional da DIVGP.
    """
    current_date = date.today()
    mes_target = mes if mes is not None else current_date.month
    ano_target = ano if ano is not None else current_date.year

    return await DivgpController.get_todas_escalas(
        session=session,
        mes=mes_target,
        ano=ano_target,
        uorg_id=uorg_id,
        uorg_pai_id=uorg_pai_id,
        status=status,
        cargo_id=cargo_id,
        search=search,
        is_admin=user_info["is_admin"]
    )
