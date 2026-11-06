from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import time, datetime

from ..resources.database import get_app_db_session
from ..auth.auth import auth_handler
from ..providers.escala_provider import EscalaProvider
from ..controllers import escala_controller

router = APIRouter(
    prefix="/api/escalas",
    tags=["Escalas"],
    dependencies=[Depends(auth_handler.decode_token)]
)

# Pydantic Schemas
class EscalaBase(BaseModel):
    inicio_jornada: time
    fim_jornada: time
    sigla: str
    codigo: Optional[str] = ""
    descricao: Optional[str] = ""
    apenas_assistenciais: bool = False

class EscalaCreate(EscalaBase):
    pass

class EscalaUpdate(EscalaBase):
    pass

class EscalaResponse(EscalaBase):
    id: int
    login: str
    data_alteracao: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Endpoints
@router.get("", response_model=List[EscalaResponse])
async def read_escalas(db: AsyncSession = Depends(get_app_db_session), current_user: dict = Depends(auth_handler.decode_token)):
    provider = EscalaProvider(db)
    return await escala_controller.listar_escalas(provider)

@router.get("/{id}", response_model=EscalaResponse)
async def read_escala(id: int, db: AsyncSession = Depends(get_app_db_session), current_user: dict = Depends(auth_handler.decode_token)):
    provider = EscalaProvider(db)
    escala = await escala_controller.obter_escala(id, provider)
    if not escala:
        raise HTTPException(status_code=404, detail="Escala não encontrada")
    return escala

@router.post("", response_model=EscalaResponse, status_code=status.HTTP_201_CREATED)
async def create_escala(
    escala: EscalaCreate, 
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    provider = EscalaProvider(db)
    
    # Validação: Sigla deve ser única
    sigla_limpa = escala.sigla.strip()
    if not sigla_limpa:
        raise HTTPException(status_code=400, detail="A sigla é obrigatória.")
    
    existing_sigla = await provider.obter_por_sigla(sigla_limpa)
    if existing_sigla:
        raise HTTPException(status_code=400, detail=f"Já existe uma escala cadastrada com a sigla '{sigla_limpa}'. A sigla deve ser única.")

    # Se código não fornecido, usa a própria sigla como código
    data = escala.model_dump()
    data["sigla"] = sigla_limpa
    if not data.get("codigo"):
        data["codigo"] = sigla_limpa

    return await escala_controller.criar_escala(data, current_user["username"], provider)

@router.put("/{id}", response_model=EscalaResponse)
async def update_escala(
    id: int, 
    escala: EscalaUpdate, 
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(auth_handler.decode_token)
):
    provider = EscalaProvider(db)
    
    # Validação: Sigla deve ser única entre escalas com id diferente
    sigla_limpa = escala.sigla.strip()
    if not sigla_limpa:
        raise HTTPException(status_code=400, detail="A sigla é obrigatória.")
        
    existing_sigla = await provider.obter_por_sigla(sigla_limpa)
    if existing_sigla and existing_sigla.id != id:
        raise HTTPException(status_code=400, detail=f"Já existe outra escala cadastrada com a sigla '{sigla_limpa}'. A sigla deve ser única.")

    data = escala.model_dump()
    data["sigla"] = sigla_limpa
    if not data.get("codigo"):
        data["codigo"] = sigla_limpa

    updated = await escala_controller.atualizar_escala(id, data, current_user["username"], provider)
    if not updated:
        raise HTTPException(status_code=404, detail="Escala não encontrada")
    return updated

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_escala(id: int, db: AsyncSession = Depends(get_app_db_session), current_user: dict = Depends(auth_handler.decode_token)):
    provider = EscalaProvider(db)
    success = await escala_controller.deletar_escala(id, provider)
    if not success:
        raise HTTPException(status_code=404, detail="Escala não encontrada")
