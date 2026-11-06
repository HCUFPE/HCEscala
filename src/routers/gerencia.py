from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from src.resources.database import get_app_db_session
from src.auth.auth import auth_handler
from src.controllers.gerencia_controller import GerenciaController

router = APIRouter(
    prefix="/api/gerencias",
    tags=["Gerências & Controle de Acesso"],
    dependencies=[Depends(auth_handler.decode_token)]
)

security = HTTPBearer()

async def get_current_user_info(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    payload = auth_handler.decode_token(token)
    username = payload.get("sub") or payload.get("username")
    groups = payload.get("groups", [])
    is_admin = (
        "GLO-SEC-HCPE-SETISD" in groups 
        or "DIVGP" in groups
        or "DIGP" in groups
        or username in ["admin", "root"]
    )
    return {"username": username, "groups": groups, "is_admin": is_admin}

# Pydantic Schemas
class UorgSimple(BaseModel):
    id: int
    codigo: Optional[str] = None
    sigla: Optional[str] = None
    nome: str
    model_config = ConfigDict(from_attributes=True)

class PostoSimple(BaseModel):
    id: int
    nome: str
    uorg: Optional[UorgSimple] = None
    model_config = ConfigDict(from_attributes=True)

class GerenciaCreate(BaseModel):
    usuario: str
    nome: str
    nivel: str # DIVGP_ADMIN, UORG, POSTO
    uorg_id: Optional[int] = None
    unidade_id: Optional[int] = None # compatibilidade
    setor_id: Optional[int] = None # compatibilidade
    posto_id: Optional[int] = None
    ativo: bool = True

class GerenciaUpdate(BaseModel):
    usuario: Optional[str] = None
    nome: Optional[str] = None
    nivel: Optional[str] = None
    uorg_id: Optional[int] = None
    unidade_id: Optional[int] = None
    setor_id: Optional[int] = None
    posto_id: Optional[int] = None
    ativo: Optional[bool] = None

class GerenciaResponse(BaseModel):
    id: int
    usuario: str
    nome: str
    nivel: str
    uorg_id: Optional[int] = None
    unidade_id: Optional[int] = None
    setor_id: Optional[int] = None
    posto_id: Optional[int] = None
    ativo: bool
    login: str
    data_alteracao: Optional[datetime] = None
    
    uorg: Optional[UorgSimple] = None
    unidade: Optional[UorgSimple] = None # compatibilidade
    setor: Optional[UorgSimple] = None # compatibilidade
    posto: Optional[PostoSimple] = None

    model_config = ConfigDict(from_attributes=True)

class UserScopeResponse(BaseModel):
    usuario: str
    is_admin: bool
    nivel: str
    descricao_escopo: str
    uorg_ids: Optional[List[int]] = None
    unidade_ids: Optional[List[int]] = None
    setor_ids: Optional[List[int]] = None
    posto_ids: Optional[List[int]] = None

@router.get("/me", response_model=UserScopeResponse)
async def get_my_scope(
    session: AsyncSession = Depends(get_app_db_session),
    user_info: dict = Depends(get_current_user_info)
):
    """
    Retorna o escopo hierárquico e as UORGs autorizadas para o usuário logado.
    """
    return await GerenciaController.get_my_scope(session, user_info["username"], user_info["groups"])

@router.get("", response_model=List[GerenciaResponse])
async def list_gerencias(
    nivel: Optional[str] = None,
    uorg_id: Optional[int] = None,
    apenas_ativos: bool = False,
    session: AsyncSession = Depends(get_app_db_session),
    user_info: dict = Depends(get_current_user_info)
):
    """
    Lista todas as atribuições de gerência (Restrito a DIVGP / Administradores).
    """
    return await GerenciaController.get_all(session, nivel, uorg_id, apenas_ativos)

@router.get("/{id}", response_model=GerenciaResponse)
async def get_gerencia(
    id: int,
    session: AsyncSession = Depends(get_app_db_session),
    user_info: dict = Depends(get_current_user_info)
):
    return await GerenciaController.get_by_id(session, id)

@router.post("", response_model=GerenciaResponse)
async def create_gerencia(
    data: GerenciaCreate,
    session: AsyncSession = Depends(get_app_db_session),
    user_info: dict = Depends(get_current_user_info)
):
    try:
        return await GerenciaController.create(session, data.model_dump(), user_info["username"], user_info["is_admin"])
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro interno ao criar gerência: {str(e)}")

@router.put("/{id}", response_model=GerenciaResponse)
async def update_gerencia(
    id: int,
    data: GerenciaUpdate,
    session: AsyncSession = Depends(get_app_db_session),
    user_info: dict = Depends(get_current_user_info)
):
    try:
        return await GerenciaController.update(session, id, data.model_dump(exclude_unset=True), user_info["username"], user_info["is_admin"])
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro interno ao atualizar gerência: {str(e)}")

@router.delete("/{id}")
async def delete_gerencia(
    id: int,
    session: AsyncSession = Depends(get_app_db_session),
    user_info: dict = Depends(get_current_user_info)
):
    return await GerenciaController.delete(session, id, user_info["is_admin"])
