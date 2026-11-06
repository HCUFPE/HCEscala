from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from src.resources.database import get_app_db_session
from src.controllers.unidade_controller import UnidadeController
from src.auth.auth import auth_handler

router = APIRouter(
    prefix="/api/unidades",
    tags=["Unidades"],
    dependencies=[Depends(auth_handler.decode_token)]
)

class SetorNestedResponse(BaseModel):
    id: int
    nome: str
    model_config = ConfigDict(from_attributes=True)

class UnidadeBase(BaseModel):
    nome: str
    setor_id: int

class UnidadeCreate(UnidadeBase):
    pass

class UnidadeUpdate(UnidadeBase):
    pass

class UnidadeResponse(UnidadeBase):
    id: int
    login: Optional[str] = ""
    data_alteracao: Optional[datetime] = None
    setor: Optional[SetorNestedResponse] = None
    model_config = ConfigDict(from_attributes=True)

@router.get("", response_model=List[UnidadeResponse])
async def get_all_unidades(session: AsyncSession = Depends(get_app_db_session)):
    return await UnidadeController.get_all(session)

@router.post("", response_model=UnidadeResponse)
async def create_unidade(
    data: UnidadeCreate, 
    session: AsyncSession = Depends(get_app_db_session),
    username: str = Depends(auth_handler.auth_wrapper)
):
    return await UnidadeController.create(session, data.model_dump(), username)

@router.put("/{id}", response_model=UnidadeResponse)
async def update_unidade(
    id: int, 
    data: UnidadeUpdate, 
    session: AsyncSession = Depends(get_app_db_session),
    username: str = Depends(auth_handler.auth_wrapper)
):
    return await UnidadeController.update(session, id, data.model_dump(), username)

@router.delete("/{id}")
async def delete_unidade(
    id: int, 
    session: AsyncSession = Depends(get_app_db_session),
    username: str = Depends(auth_handler.auth_wrapper)
):
    return await UnidadeController.delete(session, id)
