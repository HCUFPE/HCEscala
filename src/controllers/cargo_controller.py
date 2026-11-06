from ..providers.cargo_provider import CargoProvider
from typing import List, Optional

async def listar_cargos(provider: CargoProvider):
    return await provider.listar()

async def obter_cargo(id: int, provider: CargoProvider):
    return await provider.obter_por_id(id)

async def criar_cargo(data: dict, login: str, provider: CargoProvider):
    data['login'] = login or "sistema"
    return await provider.criar(data)

async def atualizar_cargo(id: int, data: dict, login: str, provider: CargoProvider):
    data['login'] = login or "sistema"
    return await provider.atualizar(id, data)

async def deletar_cargo(id: int, provider: CargoProvider) -> bool:
    from fastapi import HTTPException
    from sqlalchemy import select, func
    from ..models.funcionario import Funcionario

    stmt = select(func.count(Funcionario.id)).where(Funcionario.cargo_id == id)
    res = await provider.session.execute(stmt)
    total = res.scalar_one() or 0
    if total > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Não é possível excluir este Cargo pois existem {total} colaborador(es) vinculado(s) a ele."
        )

    return await provider.deletar(id)
