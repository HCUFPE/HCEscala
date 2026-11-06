from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.providers.setor_provider import SetorProvider

class SetorController:
    @staticmethod
    async def get_all(session: AsyncSession):
        return await SetorProvider.get_all(session)

    @staticmethod
    async def create(session: AsyncSession, data: dict, login: str):
        if not data.get("nome"):
            raise HTTPException(status_code=400, detail="O nome do setor é obrigatório.")
            
        existente = await SetorProvider.get_by_nome(session, data["nome"])
        if existente:
            raise HTTPException(status_code=400, detail="Já existe um setor com este nome.")
            
        return await SetorProvider.create(session, data, login)

    @staticmethod
    async def update(session: AsyncSession, id: int, data: dict, login: str):
        setor = await SetorProvider.get_by_id(session, id)
        if not setor:
            raise HTTPException(status_code=404, detail="Setor não encontrado.")
            
        if "nome" in data and data["nome"] != setor.nome:
            existente = await SetorProvider.get_by_nome(session, data["nome"])
            if existente:
                raise HTTPException(status_code=400, detail="Já existe um setor com este nome.")
                
        atualizado = await SetorProvider.update(session, id, data, login)
        return atualizado

    @staticmethod
    async def delete(session: AsyncSession, id: int):
        setor = await SetorProvider.get_by_id(session, id)
        if not setor:
            raise HTTPException(status_code=404, detail="Setor não encontrado.")
            
        if setor.unidades:
            raise HTTPException(status_code=400, detail="Não é possível excluir o setor pois existem unidades vinculadas a ele.")
            
        sucesso = await SetorProvider.delete(session, id)
        if not sucesso:
            raise HTTPException(status_code=500, detail="Erro ao excluir o setor.")
        return {"message": "Setor excluído com sucesso."}
