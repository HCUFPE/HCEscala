from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from pydantic import BaseModel, ConfigDict
from ..resources.database import get_app_db_session
from ..auth.auth import auth_handler
from ..models.legenda import Legenda

router = APIRouter(
    prefix="/api/legendas",
    tags=["Legendas"],
    dependencies=[Depends(auth_handler.decode_token)]
)

# Pydantic Schemas
class LegendaBase(BaseModel):
    sigla: str
    descricao: str

class LegendaCreate(LegendaBase):
    pass

class LegendaUpdate(LegendaBase):
    pass

class LegendaResponse(LegendaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# Endpoints
@router.get("", response_model=List[LegendaResponse])
async def read_legendas(db: AsyncSession = Depends(get_app_db_session)):
    result = await db.execute(select(Legenda))
    return result.scalars().all()

@router.get("/{id}", response_model=LegendaResponse)
async def read_legenda(id: int, db: AsyncSession = Depends(get_app_db_session)):
    result = await db.execute(select(Legenda).filter(Legenda.id == id))
    legenda = result.scalars().first()
    if not legenda:
        raise HTTPException(status_code=404, detail="Legenda não encontrada")
    return legenda

@router.post("", response_model=LegendaResponse, status_code=status.HTTP_201_CREATED)
async def create_legenda(legenda: LegendaCreate, db: AsyncSession = Depends(get_app_db_session)):
    # Check if sigla already exists
    result = await db.execute(select(Legenda).filter(Legenda.sigla == legenda.sigla))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Sigla já cadastrada")

    db_legenda = Legenda(**legenda.model_dump())
    db.add(db_legenda)
    await db.commit()
    await db.refresh(db_legenda)
    return db_legenda

@router.put("/{id}", response_model=LegendaResponse)
async def update_legenda(id: int, legenda: LegendaUpdate, db: AsyncSession = Depends(get_app_db_session)):
    result = await db.execute(select(Legenda).filter(Legenda.id == id))
    db_legenda = result.scalars().first()
    if not db_legenda:
        raise HTTPException(status_code=404, detail="Legenda não encontrada")

    # Check if sigla already exists in another record
    if db_legenda.sigla != legenda.sigla:
        existing = await db.execute(select(Legenda).filter(Legenda.sigla == legenda.sigla))
        if existing.scalars().first():
            raise HTTPException(status_code=400, detail="Sigla já cadastrada")

    db_legenda.sigla = legenda.sigla
    db_legenda.descricao = legenda.descricao
    await db.commit()
    await db.refresh(db_legenda)
    return db_legenda

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_legenda(id: int, db: AsyncSession = Depends(get_app_db_session)):
    result = await db.execute(select(Legenda).filter(Legenda.id == id))
    db_legenda = result.scalars().first()
    if not db_legenda:
        raise HTTPException(status_code=404, detail="Legenda não encontrada")

    await db.delete(db_legenda)
    await db.commit()
