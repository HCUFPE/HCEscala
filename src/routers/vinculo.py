from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from ..resources.database import get_app_db_session
from ..auth.auth import auth_handler
from ..providers.vinculo_provider import VinculoProvider
from ..controllers import vinculo_controller

router = APIRouter(
    prefix="/api/vinculos",
    tags=["Vinculos"],
    dependencies=[Depends(auth_handler.decode_token)]
)

# Pydantic Schemas
class VinculoBase(BaseModel):
    nome: str

class VinculoCreate(VinculoBase):
    pass

class VinculoUpdate(VinculoBase):
    pass

class VinculoResponse(VinculoBase):
    id: int
    login: str
    data_alteracao: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Endpoints
@router.get("", response_model=List[VinculoResponse])
async def read_vinculos(db: AsyncSession = Depends(get_app_db_session), current_user: dict = Depends(auth_handler.decode_token)):
    provider = VinculoProvider(db)
    return await vinculo_controller.listar_vinculos(provider)

@router.get("/{id}", response_model=VinculoResponse)
async def read_vinculo(id: int, db: AsyncSession = Depends(get_app_db_session), current_user: dict = Depends(auth_handler.decode_token)):
    provider = VinculoProvider(db)
    vinculo = await vinculo_controller.obter_vinculo(id, provider)
    if not vinculo:
        raise HTTPException(status_code=404, detail="Vínculo não encontrado")
    return vinculo

@router.post("", response_model=VinculoResponse, status_code=status.HTTP_201_CREATED)
async def create_vinculo(
    vinculo: VinculoCreate, 
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    provider = VinculoProvider(db)
    existing = await provider.obter_por_nome(vinculo.nome)
    if existing:
        raise HTTPException(status_code=400, detail="Nome de vínculo já cadastrado")
        
    return await vinculo_controller.criar_vinculo(vinculo.model_dump(), current_user["username"], provider)

@router.put("/{id}", response_model=VinculoResponse)
async def update_vinculo(
    id: int, 
    vinculo: VinculoUpdate, 
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    provider = VinculoProvider(db)
    existing = await provider.obter_por_nome(vinculo.nome)
    if existing and existing.id != id:
        raise HTTPException(status_code=400, detail="Nome de vínculo já cadastrado")
        
    updated = await vinculo_controller.atualizar_vinculo(id, vinculo.model_dump(), current_user["username"], provider)
    if not updated:
        raise HTTPException(status_code=404, detail="Vínculo não encontrado")
    return updated

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vinculo(id: int, db: AsyncSession = Depends(get_app_db_session), current_user: dict = Depends(auth_handler.decode_token)):
    provider = VinculoProvider(db)
    success = await vinculo_controller.deletar_vinculo(id, provider)
    if not success:
        raise HTTPException(status_code=404, detail="Vínculo não encontrado")
