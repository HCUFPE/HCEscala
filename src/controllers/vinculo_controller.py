from ..providers.vinculo_provider import VinculoProvider
from typing import List, Optional

async def listar_vinculos(provider: VinculoProvider):
    return await provider.listar()

async def obter_vinculo(id: int, provider: VinculoProvider):
    return await provider.obter_por_id(id)

async def criar_vinculo(data: dict, login: str, provider: VinculoProvider):
    data['login'] = login
    return await provider.criar(data)

async def atualizar_vinculo(id: int, data: dict, login: str, provider: VinculoProvider):
    data['login'] = login
    return await provider.atualizar(id, data)

async def deletar_vinculo(id: int, provider: VinculoProvider) -> bool:
    from fastapi import HTTPException
    from sqlalchemy import select, func
    from ..models.funcionario import Funcionario

    stmt = select(func.count(Funcionario.id)).where(Funcionario.vinculo_id == id)
    res = await provider.session.execute(stmt)
    total = res.scalar_one() or 0
    if total > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Não é possível excluir este Vínculo pois existem {total} colaborador(es) vinculado(s) a ele."
        )

    return await provider.deletar(id)
