from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from src.resources.database import get_app_db_session
from src.controllers.grade_controller import GradeController
from src.auth.auth import auth_handler

router = APIRouter(
    prefix="/api/grades",
    tags=["Grades"],
    dependencies=[Depends(auth_handler.decode_token)]
)

# --- Schemas ---
class GradeDiaBase(BaseModel):
    dia: int
    escala_id: Optional[int] = None
    legenda_sigla: Optional[str] = None
    descricao: Optional[str] = None

class GradeDiaCreate(GradeDiaBase):
    pass

class GradeDiaResponse(GradeDiaBase):
    id: int
    grade_id: int
    model_config = ConfigDict(from_attributes=True)

class GradeBase(BaseModel):
    funcionario_id: int
    unidade_id: int
    posto_id: Optional[int] = None
    mes: int
    ano: int
    status: Optional[str] = "Rascunho"
    observacao: Optional[str] = None

class GradeCreate(GradeBase):
    permitir_excedente: bool = False
    dias: List[GradeDiaCreate] = []

class GradeUpdate(BaseModel):
    posto_id: Optional[int] = None
    status: Optional[str] = None
    observacao: Optional[str] = None
    permitir_excedente: bool = False
    dias: Optional[List[GradeDiaCreate]] = None

class GradeResponse(GradeBase):
    id: int
    login: Optional[str] = ""
    data_alteracao: Optional[datetime] = None
    dias: List[GradeDiaResponse] = []
    model_config = ConfigDict(from_attributes=True)

class LotacaoItemInfo(BaseModel):
    unidade_id: Optional[int] = None
    unidade_nome: str
    posto_nome: str
    is_atual: bool = False

class DiaMatrixItem(BaseModel):
    dia: int
    sigla: Optional[str] = None
    escala_id: Optional[int] = None
    descricao: Optional[str] = None
    horas: float = 0.0
    is_ferias: bool = False
    is_feriado: bool = False
    feriado_nome: Optional[str] = None
    outra_unidade_sigla: Optional[str] = None
    outra_unidade_nome: Optional[str] = None
    is_outra_unidade: bool = False

class GradeMatrixItemResponse(BaseModel):
    funcionario_id: int
    matricula: str
    nome: str
    cargo: str
    cargo_id: int
    unidade_id: Optional[int] = None
    posto_id: Optional[int] = None
    escala_padrao: str
    escala_codigo: Optional[str] = "-"
    posto_nome: str
    carga_horaria_total: Optional[int] = None
    carga_horaria_semanal: int = 40
    carga_horaria_mensal_teto: float = 160.0
    total_horas_escaladas: float = 0.0
    total_horas_unidade: float = 0.0
    horas_excedentes: float = 0.0
    saldo_horas: float = 0.0
    ultrapassou_carga_horaria: bool = False
    has_multiple_lotacoes: bool = False
    total_lotacoes: int = 1
    lotacoes_info: List[LotacaoItemInfo] = []
    is_ferias_mes: bool = False
    is_diarista: bool = False
    grade_id: Optional[int] = None
    grade_status: str
    is_bloqueada: bool = False
    observacao: Optional[str] = None
    dias: List[DiaMatrixItem]

class GradeIndicatorsResponse(BaseModel):
    total_colaboradores: int
    total_ferias: int
    total_multiplas_lotacoes: int

class GradeCopyRequest(BaseModel):
    source_func_id: Optional[int] = None
    source_func_ids: Optional[List[int]] = None
    source_unidade_id: int
    source_mes: int
    source_ano: int
    target_func_ids: Optional[List[int]] = None
    target_unidade_id: Optional[int] = None
    target_posto_id: Optional[int] = None
    target_mes: Optional[int] = None
    target_ano: Optional[int] = None

class GradeDevolverRequest(BaseModel):
    motivo: Optional[str] = None

class GradeEnviarSuperiorRequest(BaseModel):
    observacao: Optional[str] = None


# --- Dependência de Usuário e Papel ---
def get_current_user_info(current_user: dict = Depends(auth_handler.decode_token)) -> dict:
    username = current_user.get("sub") or current_user.get("username") or "user"
    groups = current_user.get("groups", [])
    is_admin = ("GLO-SEC-HCPE-SETISD" in groups) or (username == "admin") or ("DIVGP." in groups)
    return {
        "username": username,
        "groups": groups,
        "is_admin": is_admin
    }


# --- Endpoints ---

@router.get("", response_model=List[GradeMatrixItemResponse])
async def get_matrix(
    mes: int = Query(..., ge=1, le=12, description="Mês da grade (1-12)"),
    ano: int = Query(..., ge=2000, le=2100, description="Ano da grade (ex: 2026)"),
    unidade_id: Optional[int] = Query(None, description="ID da Unidade"),
    cargo_id: Optional[int] = Query(None, description="Filtrar por Categoria/Cargo"),
    posto_id: Optional[int] = Query(None, description="Filtrar por Posto de Serviço"),
    search: Optional[str] = Query(None, description="Busca por nome ou matrícula"),
    status: Optional[str] = Query(None, description="Filtrar por Status (Rascunho, Enviada, Aprovada, Publicada)"),
    apenas_publicadas: bool = Query(False, description="Exibir apenas grades publicadas (Visão DIVGP.)"),
    incluir_subordinadas: bool = Query(True, description="Incluir unidades subordinadas da hierarquia"),
    session: AsyncSession = Depends(get_app_db_session),
    user_info: dict = Depends(get_current_user_info)
):
    return await GradeController.get_matrix(
        session=session,
        unidade_id=unidade_id,
        mes=mes,
        ano=ano,
        cargo_id=cargo_id,
        search_term=search,
        status_filter=status,
        apenas_publicadas=apenas_publicadas,
        posto_id=posto_id,
        incluir_subordinadas=incluir_subordinadas
    )


@router.get("/indicadores", response_model=GradeIndicatorsResponse)
async def get_indicators(
    mes: int = Query(..., ge=1, le=12),
    ano: int = Query(..., ge=2000, le=2100),
    unidade_id: Optional[int] = Query(None),
    cargo_id: Optional[int] = Query(None),
    posto_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    incluir_subordinadas: bool = Query(True),
    session: AsyncSession = Depends(get_app_db_session),
    user_info: dict = Depends(get_current_user_info)
):
    return await GradeController.get_indicators(
        session=session,
        unidade_id=unidade_id,
        mes=mes,
        ano=ano,
        posto_id=posto_id,
        cargo_id=cargo_id,
        search_term=search,
        incluir_subordinadas=incluir_subordinadas
    )


@router.get("/{id}", response_model=GradeResponse)
async def get_by_id(
    id: int,
    session: AsyncSession = Depends(get_app_db_session),
    user_info: dict = Depends(get_current_user_info)
):
    return await GradeController.get_by_id(session, id)


@router.post("", response_model=GradeResponse)
async def create(
    data: GradeCreate,
    session: AsyncSession = Depends(get_app_db_session),
    user_info: dict = Depends(get_current_user_info)
):
    return await GradeController.create(
        session=session, 
        data=data.model_dump(), 
        username=user_info["username"], 
        is_admin=user_info["is_admin"]
    )


@router.put("/{id}", response_model=GradeResponse)
async def update(
    id: int,
    data: GradeUpdate,
    session: AsyncSession = Depends(get_app_db_session),
    user_info: dict = Depends(get_current_user_info)
):
    return await GradeController.update(
        session=session, 
        id=id, 
        data=data.model_dump(exclude_unset=True), 
        username=user_info["username"], 
        is_admin=user_info["is_admin"]
    )


@router.post("/{id}/enviar-superior", response_model=GradeResponse)
async def enviar_superior(
    id: int,
    data: Optional[GradeEnviarSuperiorRequest] = None,
    session: AsyncSession = Depends(get_app_db_session),
    user_info: dict = Depends(get_current_user_info)
):
    """
    Libera/encaminha a escala para o nível hierárquico superior (UORG Pai).
    """
    observacao = data.observacao if data else None
    return await GradeController.enviar_superior(session, id, user_info["username"], observacao)


@router.post("/enviar-lote-superior")
async def enviar_lote_superior(
    unidade_id: int = Query(..., description="ID da UORG"),
    mes: int = Query(..., ge=1, le=12, description="Mês"),
    ano: int = Query(..., ge=2000, le=2100, description="Ano"),
    session: AsyncSession = Depends(get_app_db_session),
    user_info: dict = Depends(get_current_user_info)
):
    """
    Libera em lote todas as escalas de uma UORG para a chefia superior imediata.
    """
    return await GradeController.enviar_lote_superior(session, unidade_id, mes, ano, user_info["username"])


@router.post("/{id}/devolver", response_model=GradeResponse)
async def devolver_grade(
    id: int,
    data: Optional[GradeDevolverRequest] = None,
    session: AsyncSession = Depends(get_app_db_session),
    user_info: dict = Depends(get_current_user_info)
):
    """
    Devolve a escala para o gestor subordinado realizar correções.
    """
    motivo = data.motivo if data else None
    return await GradeController.devolver_grade(
        session, id, user_info["username"], motivo, user_info.get("groups")
    )


@router.post("/{id}/publicar", response_model=GradeResponse)
async def publish_grade(
    id: int,
    session: AsyncSession = Depends(get_app_db_session),
    user_info: dict = Depends(get_current_user_info)
):
    """
    Homologa e libera a escala para publicação pela DIVGP. Restrito ao gestor de nível superior mais alto da cadeia ou DIVGP.
    """
    return await GradeController.publish_grade(
        session, id, user_info["username"], user_info.get("groups"), user_info.get("is_admin", False)
    )


@router.post("/{id}/reabrir", response_model=GradeResponse)
async def reabrir_grade(
    id: int,
    session: AsyncSession = Depends(get_app_db_session),
    user_info: dict = Depends(get_current_user_info)
):
    """
    Reabre uma grade bloqueada (retorna para status 'Rascunho'). Permitido apenas para DIVGP. e Administradores.
    """
    return await GradeController.reabrir_grade(
        session=session,
        id=id,
        username=user_info["username"],
        is_admin=user_info["is_admin"]
    )


@router.post("/publicar-lote")
async def publish_all_in_unit(
    unidade_id: int = Query(..., description="ID da Unidade/UORG"),
    mes: int = Query(..., ge=1, le=12, description="Mês"),
    ano: int = Query(..., ge=2000, le=2100, description="Ano"),
    session: AsyncSession = Depends(get_app_db_session),
    user_info: dict = Depends(get_current_user_info)
):
    """
    Homologa e publica em lote todas as escalas de uma UORG para a DIVGP. Restrito ao nível mais alto da cadeia.
    """
    return await GradeController.publish_all_in_unit(
        session, unidade_id, mes, ano, user_info["username"], user_info.get("groups"), user_info.get("is_admin", False)
    )


@router.delete("/{id}")
async def delete(
    id: int,
    session: AsyncSession = Depends(get_app_db_session),
    user_info: dict = Depends(get_current_user_info)
):
    return await GradeController.delete(session, id, is_admin=user_info["is_admin"])


@router.post("/copiar", response_model=List[GradeResponse])
async def copy_grade(
    data: GradeCopyRequest,
    session: AsyncSession = Depends(get_app_db_session),
    user_info: dict = Depends(get_current_user_info)
):
    return await GradeController.copy_grade(
        session=session, 
        data=data.model_dump(), 
        username=user_info["username"], 
        is_admin=user_info["is_admin"]
    )
