from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.providers.unidade_provider import UnidadeProvider
from src.providers.setor_provider import SetorProvider

class UnidadeController:
    @staticmethod
    async def get_all(session: AsyncSession):
        return await UnidadeProvider.get_all(session)

    @staticmethod
    async def create(session: AsyncSession, data: dict, login: str):
        if not data.get("nome"):
            raise HTTPException(status_code=400, detail="O nome da unidade é obrigatório.")
        if not data.get("setor_id"):
            raise HTTPException(status_code=400, detail="O setor_id é obrigatório.")
            
        setor = await SetorProvider.get_by_id(session, data["setor_id"])
        if not setor:
            raise HTTPException(status_code=400, detail="Setor não encontrado.")
            
        existente = await UnidadeProvider.get_by_nome(session, data["nome"])
        if existente:
            raise HTTPException(status_code=400, detail="Já existe uma unidade com este nome.")
            
        return await UnidadeProvider.create(session, data, login)

    @staticmethod
    async def update(session: AsyncSession, id: int, data: dict, login: str):
        unidade = await UnidadeProvider.get_by_id(session, id)
        if not unidade:
            raise HTTPException(status_code=404, detail="Unidade não encontrada.")
            
        if "setor_id" in data and data["setor_id"] != unidade.setor_id:
            setor = await SetorProvider.get_by_id(session, data["setor_id"])
            if not setor:
                raise HTTPException(status_code=400, detail="Setor não encontrado.")
                
        if "nome" in data and data["nome"] != unidade.nome:
            existente = await UnidadeProvider.get_by_nome(session, data["nome"])
            if existente:
                raise HTTPException(status_code=400, detail="Já existe uma unidade com este nome.")
                
        atualizado = await UnidadeProvider.update(session, id, data, login)
        return atualizado

    @staticmethod
    async def delete(session: AsyncSession, id: int):
        unidade = await UnidadeProvider.get_by_id(session, id)
        if not unidade:
            raise HTTPException(status_code=404, detail="Unidade não encontrada.")
            
        if unidade.postos:
            raise HTTPException(status_code=400, detail="Não é possível excluir a unidade pois existem postos vinculados a ela.")
            
        sucesso = await UnidadeProvider.delete(session, id)
        if not sucesso:
            raise HTTPException(status_code=500, detail="Erro ao excluir a unidade.")
        return {"message": "Unidade excluída com sucesso."}
