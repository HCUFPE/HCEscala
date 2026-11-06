from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
from src.resources.database import get_app_db_session
from src.auth.auth import auth_handler
from src.controllers.feriado_controller import FeriadoController

router = APIRouter(
    prefix="/api/feriados",
    tags=["Feriados"],
    dependencies=[Depends(auth_handler.decode_token)]
)

class FeriadoBase(BaseModel):
    nome: str
    data: date
    tipo: str

class FeriadoCreate(FeriadoBase):
    pass

class FeriadoUpdate(BaseModel):
    nome: Optional[str] = None
    data: Optional[date] = None
    tipo: Optional[str] = None

class FeriadoResponse(FeriadoBase):
    id: int

    class Config:
        orm_mode = True

@router.get("", response_model=List[FeriadoResponse])
async def list_feriados(
    ano: Optional[int] = None,
    session: AsyncSession = Depends(get_app_db_session),
    user: str = Depends(auth_handler.auth_wrapper)
):
    return await FeriadoController.get_all(session, ano)

@router.get("/{id}", response_model=FeriadoResponse)
async def get_feriado(
    id: int,
    session: AsyncSession = Depends(get_app_db_session),
    user: str = Depends(auth_handler.auth_wrapper)
):
    return await FeriadoController.get_by_id(session, id)

@router.post("", response_model=FeriadoResponse)
async def create_feriado(
    feriado: FeriadoCreate,
    session: AsyncSession = Depends(get_app_db_session),
    user: str = Depends(auth_handler.auth_wrapper)
):
    return await FeriadoController.create(session, feriado.dict(), user)

@router.put("/{id}", response_model=FeriadoResponse)
async def update_feriado(
    id: int,
    feriado: FeriadoUpdate,
    session: AsyncSession = Depends(get_app_db_session),
    user: str = Depends(auth_handler.auth_wrapper)
):
    return await FeriadoController.update(session, id, feriado.dict(exclude_unset=True), user)

@router.delete("/{id}")
async def delete_feriado(
    id: int,
    session: AsyncSession = Depends(get_app_db_session),
    user: str = Depends(auth_handler.auth_wrapper)
):
    return await FeriadoController.delete(session, id)
