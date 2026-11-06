from typing import List, Optional
from ..providers.escala_provider import EscalaProvider
from ..models.escala import Escala

async def listar_escalas(provider: EscalaProvider) -> List[Escala]:
    return await provider.listar()

async def obter_escala(id: int, provider: EscalaProvider) -> Optional[Escala]:
    return await provider.obter_por_id(id)

async def criar_escala(data: dict, login: str, provider: EscalaProvider) -> Escala:
    data['login'] = login
    return await provider.criar(data)

async def atualizar_escala(id: int, data: dict, login: str, provider: EscalaProvider) -> Optional[Escala]:
    data['login'] = login
    return await provider.atualizar(id, data)

async def deletar_escala(id: int, provider: EscalaProvider) -> bool:
    from fastapi import HTTPException
    from sqlalchemy import select, func
    from ..models.funcionario import Funcionario
    from ..models.grade import GradeDia

    # 1. Colaboradores com esta escala como padrão
    stmt_func = select(func.count(Funcionario.id)).where(Funcionario.escala_id == id)
    res_func = await provider.session.execute(stmt_func)
    total_func = res_func.scalar_one() or 0
    if total_func > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Não é possível excluir esta Escala pois existem {total_func} colaborador(es) associados a ela como escala padrão."
        )

    # 2. Dias de grade de escalas utilizando esta escala
    stmt_dias = select(func.count(GradeDia.id)).where(GradeDia.escala_id == id)
    res_dias = await provider.session.execute(stmt_dias)
    total_dias = res_dias.scalar_one() or 0
    if total_dias > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Não é possível excluir esta Escala pois ela foi utilizada em {total_dias} lançamento(s) de dia em grades de serviço."
        )

    return await provider.deletar(id)
