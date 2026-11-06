from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.providers.posto_provider import PostoProvider
from src.providers.uorg_provider import UorgProvider

class PostoController:
    @staticmethod
    async def get_all(session: AsyncSession):
        return await PostoProvider.get_all(session)

    @staticmethod
    async def get_by_uorg(session: AsyncSession, uorg_id: int):
        return await PostoProvider.get_by_uorg(session, uorg_id)

    @staticmethod
    async def create(session: AsyncSession, data: dict, login: str):
        raw_nome = data.get("nome", "")
        if not raw_nome or not raw_nome.strip():
            raise HTTPException(status_code=400, detail="O nome do Posto de Serviço é obrigatório e não pode ser em branco.")
        
        uorg_id = data.get("uorg_id") or data.get("unidade_id")
        if not uorg_id:
            raise HTTPException(status_code=400, detail="A Unidade Organizacional (UORG Pai) é obrigatória.")
        
        nome = raw_nome.strip().upper()
        data["nome"] = nome
        data["uorg_id"] = uorg_id
        data["unidade_id"] = uorg_id
            
        uorg = await UorgProvider.get_by_id(session, uorg_id)
        if not uorg:
            raise HTTPException(status_code=400, detail="Unidade Organizacional vinculada não encontrada.")
            
        existente = await PostoProvider.get_by_nome_and_uorg(session, nome, uorg_id)
        if existente:
            raise HTTPException(status_code=400, detail="Já existe um Posto de Serviço com este nome nesta Unidade Organizacional.")
            
        return await PostoProvider.create(session, data, login)

    @staticmethod
    async def update(session: AsyncSession, id: int, data: dict, login: str):
        posto = await PostoProvider.get_by_id(session, id)
        if not posto:
            raise HTTPException(status_code=404, detail="Posto não encontrado.")
            
        uorg_id = data.get("uorg_id") or data.get("unidade_id") or posto.uorg_id
        data["uorg_id"] = uorg_id
        data["unidade_id"] = uorg_id

        if uorg_id != posto.uorg_id:
            uorg = await UorgProvider.get_by_id(session, uorg_id)
            if not uorg:
                raise HTTPException(status_code=400, detail="Unidade Organizacional vinculada não encontrada.")
                
        if "nome" in data:
            raw_nome = data.get("nome", "")
            if not raw_nome or not raw_nome.strip():
                raise HTTPException(status_code=400, detail="O nome do Posto de Serviço é obrigatório e não pode ser em branco.")
            new_nome = raw_nome.strip().upper()
            data["nome"] = new_nome
        else:
            new_nome = posto.nome

        if new_nome != posto.nome or uorg_id != posto.uorg_id:
            existente = await PostoProvider.get_by_nome_and_uorg(session, new_nome, uorg_id)
            if existente and existente.id != id:
                raise HTTPException(status_code=400, detail="Já existe um Posto de Serviço com este nome nesta Unidade Organizacional.")
                
        atualizado = await PostoProvider.update(session, id, data, login)
        return atualizado

    @staticmethod
    async def delete(session: AsyncSession, id: int):
        posto = await PostoProvider.get_by_id(session, id)
        if not posto:
            raise HTTPException(status_code=404, detail="Posto não encontrado.")

        from sqlalchemy import select, func
        from src.models.funcionario_lotacao import FuncionarioLotacao
        from src.models.grade import Grade
        from src.models.usuario_gerencia import UsuarioGerencia

        # 1. Validação cruzada: Funcionários com lotação associada a este Posto
        stmt_lotacoes = select(func.count(FuncionarioLotacao.id)).where(FuncionarioLotacao.posto_id == id)
        res_lot = await session.execute(stmt_lotacoes)
        total_lotacoes = res_lot.scalar_one() or 0
        if total_lotacoes > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Não é possível excluir este Posto de Serviço pois existem {total_lotacoes} colaborador(es) com lotação associada a ele. Remova ou altere as lotações primeiro."
            )

        # 2. Validação cruzada: Grades de escala com este Posto
        stmt_grades = select(func.count(Grade.id)).where(Grade.posto_id == id)
        res_grades = await session.execute(stmt_grades)
        total_grades = res_grades.scalar_one() or 0
        if total_grades > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Não é possível excluir este Posto de Serviço pois existem {total_grades} grade(s) de escala gerada(s) vinculadas a ele."
            )

        # 3. Validação cruzada: Delegações de gerência vinculadas a este Posto
        stmt_ger = select(func.count(UsuarioGerencia.id)).where(UsuarioGerencia.posto_id == id)
        res_ger = await session.execute(stmt_ger)
        total_ger = res_ger.scalar_one() or 0
        if total_ger > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Não é possível excluir este Posto de Serviço pois existem {total_ger} delegação(ões) de chefia vinculada(s) a ele."
            )
            
        sucesso = await PostoProvider.delete(session, id)
        if not sucesso:
            raise HTTPException(status_code=500, detail="Erro ao excluir o posto.")
        return {"message": "Posto excluído com sucesso."}

    @staticmethod
    async def delete_all(session: AsyncSession, login: str = "sistema"):
        """
        Remove todos os Postos de Serviço do sistema, desvinculando de lotações, gerências e grades.
        """
        from sqlalchemy import text
        await session.execute(text("UPDATE funcionarios_lotacoes SET posto_id = NULL WHERE posto_id IS NOT NULL"))
        await session.execute(text("UPDATE usuario_gerencias SET posto_id = NULL WHERE posto_id IS NOT NULL"))
        await session.execute(text("UPDATE grades SET posto_id = NULL WHERE posto_id IS NOT NULL"))
        result = await session.execute(text("DELETE FROM postos"))
        total_removidos = result.rowcount
        await session.commit()
        return {
            "status": "success",
            "message": f"Todos os {total_removidos} postos de serviço foram removidos com sucesso.",
            "total_removidos": total_removidos
        }
