from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from src.resources.database import get_app_db_session
from src.controllers.posto_controller import PostoController
from src.auth.auth import auth_handler

router = APIRouter(
    prefix="/api/postos",
    tags=["Postos de Serviço"],
    dependencies=[Depends(auth_handler.decode_token)]
)

class UorgSimpleResponse(BaseModel):
    id: int
    codigo: Optional[str] = None
    sigla: Optional[str] = None
    nome: str
    uorg_pai_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class PostoBase(BaseModel):
    nome: str
    uorg_id: Optional[int] = None
    unidade_id: Optional[int] = None

class PostoCreate(BaseModel):
    nome: str
    uorg_id: Optional[int] = None
    unidade_id: Optional[int] = None

class PostoUpdate(BaseModel):
    nome: Optional[str] = None
    uorg_id: Optional[int] = None
    unidade_id: Optional[int] = None

class PostoResponse(BaseModel):
    id: int
    nome: str
    uorg_id: Optional[int] = None
    unidade_id: Optional[int] = None
    login: Optional[str] = ""
    data_alteracao: Optional[datetime] = None
    uorg: Optional[UorgSimpleResponse] = None
    model_config = ConfigDict(from_attributes=True)

@router.get("", response_model=List[PostoResponse])
async def get_all_postos(session: AsyncSession = Depends(get_app_db_session)):
    return await PostoController.get_all(session)

@router.get("/uorg/{uorg_id}", response_model=List[PostoResponse])
async def get_postos_by_uorg(uorg_id: int, session: AsyncSession = Depends(get_app_db_session)):
    return await PostoController.get_by_uorg(session, uorg_id)

@router.post("", response_model=PostoResponse)
async def create_posto(
    data: PostoCreate, 
    session: AsyncSession = Depends(get_app_db_session),
    username: str = Depends(auth_handler.auth_wrapper)
):
    return await PostoController.create(session, data.model_dump(), username)

@router.put("/{id}", response_model=PostoResponse)
async def update_posto(
    id: int, 
    data: PostoUpdate, 
    session: AsyncSession = Depends(get_app_db_session),
    username: str = Depends(auth_handler.auth_wrapper)
):
    return await PostoController.update(session, id, data.model_dump(exclude_unset=True), username)

@router.delete("/all")
async def delete_all_postos(
    session: AsyncSession = Depends(get_app_db_session),
    username: str = Depends(auth_handler.auth_wrapper)
):
    """
    Remove todos os postos de serviço cadastrados.
    """
    return await PostoController.delete_all(session, username)


@router.delete("/{id}")
async def delete_posto(
    id: int, 
    session: AsyncSession = Depends(get_app_db_session),
    username: str = Depends(auth_handler.auth_wrapper)
):
    return await PostoController.delete(session, id)
