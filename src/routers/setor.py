from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from src.resources.database import get_app_db_session
from src.controllers.setor_controller import SetorController
from src.auth.auth import auth_handler

router = APIRouter(
    prefix="/api/setores",
    tags=["Setores"],
    dependencies=[Depends(auth_handler.decode_token)]
)

class SetorBase(BaseModel):
    nome: str

class SetorCreate(SetorBase):
    pass

class SetorUpdate(SetorBase):
    pass

class SetorResponse(SetorBase):
    id: int
    login: Optional[str] = ""
    data_alteracao: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

@router.get("", response_model=List[SetorResponse])
async def get_all_setores(session: AsyncSession = Depends(get_app_db_session)):
    return await SetorController.get_all(session)

@router.post("", response_model=SetorResponse)
async def create_setor(
    data: SetorCreate, 
    session: AsyncSession = Depends(get_app_db_session),
    username: str = Depends(auth_handler.auth_wrapper)
):
    return await SetorController.create(session, data.model_dump(), username)

@router.put("/{id}", response_model=SetorResponse)
async def update_setor(
    id: int, 
    data: SetorUpdate, 
    session: AsyncSession = Depends(get_app_db_session),
    username: str = Depends(auth_handler.auth_wrapper)
):
    return await SetorController.update(session, id, data.model_dump(), username)

@router.delete("/{id}")
async def delete_setor(
    id: int, 
    session: AsyncSession = Depends(get_app_db_session),
    username: str = Depends(auth_handler.auth_wrapper)
):
    return await SetorController.delete(session, id)
