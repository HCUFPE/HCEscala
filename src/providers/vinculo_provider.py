from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.vinculo import Vinculo
from typing import List, Optional

class VinculoProvider:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def listar(self) -> List[Vinculo]:
        result = await self.session.execute(select(Vinculo))
        return result.scalars().all()

    async def obter_por_id(self, id: int) -> Optional[Vinculo]:
        result = await self.session.execute(select(Vinculo).where(Vinculo.id == id))
        return result.scalars().first()

    async def obter_por_nome(self, nome: str) -> Optional[Vinculo]:
        result = await self.session.execute(select(Vinculo).where(Vinculo.nome == nome))
        return result.scalars().first()

    async def criar(self, data: dict) -> Vinculo:
        vinculo = Vinculo(**data)
        self.session.add(vinculo)
        await self.session.commit()
        await self.session.refresh(vinculo)
        return vinculo

    async def atualizar(self, id: int, data: dict) -> Optional[Vinculo]:
        vinculo = await self.obter_por_id(id)
        if not vinculo:
            return None
        
        for key, value in data.items():
            setattr(vinculo, key, value)
            
        await self.session.commit()
        await self.session.refresh(vinculo)
        return vinculo

    async def deletar(self, id: int) -> bool:
        vinculo = await self.obter_por_id(id)
        if not vinculo:
            return False
            
        await self.session.delete(vinculo)
        await self.session.commit()
        return True
