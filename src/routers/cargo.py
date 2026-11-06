from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from ..resources.database import get_app_db_session
from ..auth.auth import auth_handler
from ..providers.cargo_provider import CargoProvider
from ..controllers import cargo_controller

router = APIRouter(
    prefix="/api/cargos",
    tags=["Cargos"],
    dependencies=[Depends(auth_handler.decode_token)]
)

# Pydantic Schemas
class CargoBase(BaseModel):
    nome: str

class CargoCreate(CargoBase):
    pass

class CargoUpdate(CargoBase):
    pass

class CargoResponse(CargoBase):
    id: int
    login: str
    data_alteracao: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Endpoints
@router.get("", response_model=List[CargoResponse])
async def read_cargos(db: AsyncSession = Depends(get_app_db_session), current_user: dict = Depends(auth_handler.decode_token)):
    provider = CargoProvider(db)
    return await cargo_controller.listar_cargos(provider)

@router.get("/{id}", response_model=CargoResponse)
async def read_cargo(id: int, db: AsyncSession = Depends(get_app_db_session), current_user: dict = Depends(auth_handler.decode_token)):
    provider = CargoProvider(db)
    cargo = await cargo_controller.obter_cargo(id, provider)
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo não encontrado")
    return cargo

@router.post("", response_model=CargoResponse, status_code=status.HTTP_201_CREATED)
async def create_cargo(
    cargo: CargoCreate, 
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    provider = CargoProvider(db)
    nome_limpo = cargo.nome.strip()
    if not nome_limpo:
        raise HTTPException(status_code=400, detail="O nome do cargo não pode ficar em branco.")

    existing = await provider.obter_por_nome(nome_limpo)
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Já existe o cargo '{nome_limpo}' cadastrado."
        )
        
    cargo_data = cargo.model_dump()
    cargo_data["nome"] = nome_limpo
    username = current_user.get("username") or current_user.get("sub") or "sistema"
    try:
        return await cargo_controller.criar_cargo(cargo_data, username, provider)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao salvar cargo: {str(e)}")

@router.put("/{id}", response_model=CargoResponse)
async def update_cargo(
    id: int, 
    cargo: CargoUpdate, 
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    provider = CargoProvider(db)
    nome_limpo = cargo.nome.strip()
    if not nome_limpo:
        raise HTTPException(status_code=400, detail="O nome do cargo não pode ficar em branco.")

    existing = await provider.obter_por_nome(nome_limpo)
    if existing and existing.id != id:
        raise HTTPException(
            status_code=400, 
            detail=f"Já existe o cargo '{nome_limpo}' cadastrado."
        )
        
    cargo_data = cargo.model_dump()
    cargo_data["nome"] = nome_limpo
    username = current_user.get("username") or current_user.get("sub") or "sistema"
    try:
        updated = await cargo_controller.atualizar_cargo(id, cargo_data, username, provider)
        if not updated:
            raise HTTPException(status_code=404, detail="Cargo não encontrado")
        return updated
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao atualizar cargo: {str(e)}")

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cargo(id: int, db: AsyncSession = Depends(get_app_db_session), current_user: dict = Depends(auth_handler.decode_token)):
    provider = CargoProvider(db)
    success = await cargo_controller.deletar_cargo(id, provider)
    if not success:
        raise HTTPException(status_code=404, detail="Cargo não encontrado")
