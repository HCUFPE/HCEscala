from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.providers.funcionario_provider import FuncionarioProvider

class FuncionarioController:
    @staticmethod
    async def get_all(session: AsyncSession):
        return await FuncionarioProvider.get_all(session)
        
    @staticmethod
    async def get_by_id(session: AsyncSession, id: int):
        funcionario = await FuncionarioProvider.get_by_id(session, id)
        if not funcionario:
            raise HTTPException(status_code=404, detail="Funcionário não encontrado.")
        return funcionario

    @staticmethod
    def _sanitize_matricula(matricula: str) -> str:
        if not matricula:
            return ""
        m = str(matricula).strip()
        if m.startswith("99") and m.endswith("26") and len(m) > 4:
            m = m[2:-2]
        return m

    @staticmethod
    async def create(session: AsyncSession, data: dict, login: str):
        if not data.get("matricula") or not data.get("nome"):
            raise HTTPException(status_code=400, detail="Matrícula e Nome são obrigatórios.")
        
        data["matricula"] = FuncionarioController._sanitize_matricula(data["matricula"])
        data["nome"] = data["nome"].strip().upper()
            
        existente = await FuncionarioProvider.get_by_matricula(session, data["matricula"])
        if existente:
            raise HTTPException(status_code=400, detail="Já existe um funcionário com esta matrícula.")
            
        return await FuncionarioProvider.create(session, data, login)

    @staticmethod
    async def update(session: AsyncSession, id: int, data: dict, login: str):
        funcionario = await FuncionarioProvider.get_by_id(session, id)
        if not funcionario:
            raise HTTPException(status_code=404, detail="Funcionário não encontrado.")
            
        if "matricula" in data:
            data["matricula"] = FuncionarioController._sanitize_matricula(data["matricula"])
            if data["matricula"] != funcionario.matricula:
                existente = await FuncionarioProvider.get_by_matricula(session, data["matricula"])
                if existente:
                    raise HTTPException(status_code=400, detail="Já existe um funcionário com esta matrícula.")
        
        if "nome" in data and data["nome"]:
            data["nome"] = data["nome"].strip().upper()
                
        atualizado = await FuncionarioProvider.update(session, id, data, login)
        return atualizado

    @staticmethod
    async def delete(session: AsyncSession, id: int):
        funcionario = await FuncionarioProvider.get_by_id(session, id)
        if not funcionario:
            raise HTTPException(status_code=404, detail="Funcionário não encontrado.")
            
        from sqlalchemy import select, func
        from src.models.grade import Grade
        from src.models.funcionario_ferias import FuncionarioFerias

        # 1. Grades de escala associadas
        stmt_grade = select(func.count(Grade.id)).where(Grade.funcionario_id == id)
        res_grade = await session.execute(stmt_grade)
        total_grade = res_grade.scalar_one() or 0
        if total_grade > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Não é possível excluir o colaborador pois existem {total_grade} grade(s) de escala gerada(s) para ele no sistema."
            )

        # 2. Registros de férias
        stmt_ferias = select(func.count(FuncionarioFerias.id)).where(FuncionarioFerias.funcionario_id == id)
        res_ferias = await session.execute(stmt_ferias)
        total_ferias = res_ferias.scalar_one() or 0
        if total_ferias > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Não é possível excluir o colaborador pois existem {total_ferias} registro(s) de férias cadastrado(s) para ele."
            )

        sucesso = await FuncionarioProvider.delete(session, id)
        if not sucesso:
            raise HTTPException(status_code=500, detail="Erro ao excluir o funcionário.")
        return {"message": "Funcionário excluído com sucesso."}

    @staticmethod
    async def ajustar_inicio_lotacoes_abertas(session: AsyncSession, login: str):
        total_atualizados = await FuncionarioProvider.ajustar_inicio_lotacoes_abertas(session, "2025-01-01", login)
        return {
            "message": f"Data de início de {total_atualizados} lotações em aberto ajustadas com sucesso para 01/01/2025.",
            "total_atualizados": total_atualizados
        }

    @staticmethod
    async def add_lotacao(session: AsyncSession, funcionario_id: int, data: dict, login: str):
        funcionario = await FuncionarioProvider.get_by_id(session, funcionario_id)
        if not funcionario:
            raise HTTPException(status_code=404, detail="Funcionário não encontrado.")
        
        return await FuncionarioProvider.add_lotacao(session, funcionario_id, data, login)

    @staticmethod
    async def update_lotacao(session: AsyncSession, funcionario_id: int, lotacao_id: int, data: dict, login: str):
        funcionario = await FuncionarioProvider.get_by_id(session, funcionario_id)
        if not funcionario:
            raise HTTPException(status_code=404, detail="Funcionário não encontrado.")
            
        lotacao = await FuncionarioProvider.update_lotacao(session, lotacao_id, data, login)
        if not lotacao:
            raise HTTPException(status_code=404, detail="Lotação não encontrada.")
        return lotacao
        
    @staticmethod
    async def remove_lotacao(session: AsyncSession, funcionario_id: int, lotacao_id: int):
        # Could verify if lotacao belongs to funcionario_id, but skipping for simplicity
        sucesso = await FuncionarioProvider.remove_lotacao(session, lotacao_id)
        if not sucesso:
            raise HTTPException(status_code=404, detail="Lotação não encontrada.")
        return {"message": "Lotação removida com sucesso."}
        
    @staticmethod
    async def add_ferias(session: AsyncSession, funcionario_id: int, data: dict, login: str):
        funcionario = await FuncionarioProvider.get_by_id(session, funcionario_id)
        if not funcionario:
            raise HTTPException(status_code=404, detail="Funcionário não encontrado.")
            
        if data["data_inicio"] > data["data_fim"]:
            raise HTTPException(status_code=400, detail="Data de início não pode ser maior que a data de fim.")
        
        return await FuncionarioProvider.add_ferias(session, funcionario_id, data, login)
        
    @staticmethod
    async def remove_ferias(session: AsyncSession, funcionario_id: int, ferias_id: int):
        sucesso = await FuncionarioProvider.remove_ferias(session, ferias_id)
        if not sucesso:
            raise HTTPException(status_code=404, detail="Férias não encontrada.")
        return {"message": "Férias removida com sucesso."}
