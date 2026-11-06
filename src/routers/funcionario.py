from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict
from src.resources.database import get_app_db_session
from src.controllers.funcionario_controller import FuncionarioController
from src.auth.auth import auth_handler

router = APIRouter(
    prefix="/api/funcionarios",
    tags=["Funcionarios"],
    dependencies=[Depends(auth_handler.decode_token)]
)

# --- Schemas ---
class CargoNested(BaseModel):
    id: int
    nome: Optional[str] = ""
    model_config = ConfigDict(from_attributes=True)

class EscalaNested(BaseModel):
    id: int
    codigo: Optional[str] = ""
    sigla: Optional[str] = ""
    descricao: Optional[str] = ""
    model_config = ConfigDict(from_attributes=True)

class VinculoNested(BaseModel):
    id: int
    nome: Optional[str] = ""
    model_config = ConfigDict(from_attributes=True)

class UorgNested(BaseModel):
    id: int
    codigo: Optional[str] = None
    sigla: Optional[str] = None
    nome: Optional[str] = ""
    model_config = ConfigDict(from_attributes=True)

class UnidadeNested(BaseModel):
    id: int
    nome: Optional[str] = ""
    model_config = ConfigDict(from_attributes=True)

class PostoNested(BaseModel):
    id: int
    nome: Optional[str] = ""
    model_config = ConfigDict(from_attributes=True)

# Lotacao
class FuncionarioLotacaoBase(BaseModel):
    uorg_id: Optional[int] = None
    unidade_id: Optional[int] = None
    posto_id: Optional[int] = None
    data_inicio: date
    data_fim: Optional[date] = None

class FuncionarioLotacaoCreate(FuncionarioLotacaoBase):
    pass

class FuncionarioLotacaoUpdate(BaseModel):
    uorg_id: Optional[int] = None
    unidade_id: Optional[int] = None
    posto_id: Optional[int] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None

class FuncionarioLotacaoResponse(FuncionarioLotacaoBase):
    id: int
    uorg: Optional[UorgNested] = None
    unidade: Optional[UnidadeNested] = None
    posto: Optional[PostoNested] = None
    model_config = ConfigDict(from_attributes=True)

# Ferias
class FuncionarioFeriasBase(BaseModel):
    data_inicio: date
    data_fim: date

class FuncionarioFeriasCreate(FuncionarioFeriasBase):
    pass

class FuncionarioFeriasResponse(FuncionarioFeriasBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Funcionario
class FuncionarioBase(BaseModel):
    matricula: str
    nome: str
    carga_horaria: int = 40
    cargo_id: int
    escala_id: int
    vinculo_id: Optional[int] = None

class FuncionarioCreate(FuncionarioBase):
    pass

class FuncionarioUpdate(BaseModel):
    matricula: Optional[str] = None
    nome: Optional[str] = None
    carga_horaria: Optional[int] = None
    cargo_id: Optional[int] = None
    escala_id: Optional[int] = None
    vinculo_id: Optional[int] = None

class FuncionarioResponse(FuncionarioBase):
    id: int
    cargo: Optional[CargoNested] = None
    escala: Optional[EscalaNested] = None
    vinculo: Optional[VinculoNested] = None
    lotacoes: List[FuncionarioLotacaoResponse] = []
    ferias: List[FuncionarioFeriasResponse] = []
    login: Optional[str] = ""
    data_alteracao: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

# --- Routes ---
@router.get("", response_model=List[FuncionarioResponse])
async def get_all(session: AsyncSession = Depends(get_app_db_session)):
    return await FuncionarioController.get_all(session)

@router.get("/{id}", response_model=FuncionarioResponse)
async def get_by_id(id: int, session: AsyncSession = Depends(get_app_db_session)):
    return await FuncionarioController.get_by_id(session, id)

@router.post("", response_model=FuncionarioResponse)
async def create(
    data: FuncionarioCreate, 
    session: AsyncSession = Depends(get_app_db_session),
    username: str = Depends(auth_handler.auth_wrapper)
):
    return await FuncionarioController.create(session, data.model_dump(), username)

@router.put("/{id}", response_model=FuncionarioResponse)
async def update(
    id: int, 
    data: FuncionarioUpdate, 
    session: AsyncSession = Depends(get_app_db_session),
    username: str = Depends(auth_handler.auth_wrapper)
):
    return await FuncionarioController.update(session, id, data.model_dump(exclude_unset=True), username)

@router.delete("/{id}")
async def delete(
    id: int, 
    session: AsyncSession = Depends(get_app_db_session),
    username: str = Depends(auth_handler.auth_wrapper)
):
    return await FuncionarioController.delete(session, id)

@router.post("/lotacoes/ajustar-inicio-abertas")
async def ajustar_inicio_lotacoes_abertas(
    session: AsyncSession = Depends(get_app_db_session),
    username: str = Depends(auth_handler.auth_wrapper)
):
    return await FuncionarioController.ajustar_inicio_lotacoes_abertas(session, username)

# --- Routes for Lotacao ---
@router.post("/{id}/lotacoes", response_model=FuncionarioLotacaoResponse)
async def add_lotacao(
    id: int,
    data: FuncionarioLotacaoCreate,
    session: AsyncSession = Depends(get_app_db_session),
    username: str = Depends(auth_handler.auth_wrapper)
):
    return await FuncionarioController.add_lotacao(session, id, data.model_dump(), username)

@router.put("/{id}/lotacoes/{lotacao_id}", response_model=FuncionarioLotacaoResponse)
async def update_lotacao(
    id: int,
    lotacao_id: int,
    data: FuncionarioLotacaoUpdate,
    session: AsyncSession = Depends(get_app_db_session),
    username: str = Depends(auth_handler.auth_wrapper)
):
    return await FuncionarioController.update_lotacao(session, id, lotacao_id, data.model_dump(exclude_unset=True), username)

@router.delete("/{id}/lotacoes/{lotacao_id}")
async def remove_lotacao(
    id: int,
    lotacao_id: int,
    session: AsyncSession = Depends(get_app_db_session),
    username: str = Depends(auth_handler.auth_wrapper)
):
    return await FuncionarioController.remove_lotacao(session, id, lotacao_id)

# --- Routes for Ferias ---
@router.post("/{id}/ferias", response_model=FuncionarioFeriasResponse)
async def add_ferias(
    id: int,
    data: FuncionarioFeriasCreate,
    session: AsyncSession = Depends(get_app_db_session),
    username: str = Depends(auth_handler.auth_wrapper)
):
    return await FuncionarioController.add_ferias(session, id, data.model_dump(), username)

@router.delete("/{id}/ferias/{ferias_id}")
async def remove_ferias(
    id: int,
    ferias_id: int,
    session: AsyncSession = Depends(get_app_db_session),
    username: str = Depends(auth_handler.auth_wrapper)
):
    return await FuncionarioController.remove_ferias(session, id, ferias_id)

@router.post("/importar-onedrive")
async def importar_onedrive(
    session: AsyncSession = Depends(get_app_db_session),
    username: str = Depends(auth_handler.auth_wrapper)
):
    import os
    from src.helpers.funcionario_importer import FuncionarioImporter

    onedrive_path = r"C:\Users\marcio.gomes.1\OneDrive - EBSERH\Documentos(1)\Arquivo de importação para o aplicativo de escala.xlsx"
    local_path = r"c:\Users\marcio.gomes.1\.gemini\antigravity-ide\scratch\appgrade\importacao_escala.xlsx"
    
    file_to_use = onedrive_path if os.path.exists(onedrive_path) else local_path
    if not os.path.exists(file_to_use):
        raise HTTPException(status_code=400, detail="Arquivo Excel não encontrado no caminho especificado.")

    return await FuncionarioImporter.import_from_excel(
        session=session,
        file_path_or_bytes=file_to_use,
        login=username,
        sheet_target="Relação nominal trabalhador"
    )

