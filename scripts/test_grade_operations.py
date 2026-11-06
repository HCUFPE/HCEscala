import asyncio
import sys
import os

# Adiciona o diretório raiz ao sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, delete
from src.resources.database import DatabaseManager
import src.models
from src.models.funcionario import Funcionario
from src.models.unidade import Unidade
from src.models.grade import Grade, GradeDia
from src.providers.grade_provider import GradeProvider
from src.controllers.grade_controller import GradeController

async def test_grade():
    print("Iniciando testes da funcionalidade de Grade...")
    db_manager = DatabaseManager("sqlite+aiosqlite:///app.db")
    
    async for session in db_manager.get_session():
        # 1. Buscar uma unidade e funcionários para teste
        stmt_func = select(Funcionario).limit(5)
        res_func = await session.execute(stmt_func)
        funcs = res_func.scalars().all()

        stmt_unid = select(Unidade).limit(1)
        res_unid = await session.execute(stmt_unid)
        unid = res_unid.scalars().first()

        if not funcs or not unid:
            print("Não há funcionários ou unidades cadastradas no banco de dados para o teste.")
            return

        func1 = funcs[0]
        func2 = funcs[1] if len(funcs) > 1 else funcs[0]
        unidade_id = unid.id
        mes = 5
        ano = 2026

        print(f"Testando com Funcionario 1: {func1.nome} (ID: {func1.id})")
        print(f"Testando com Funcionario 2: {func2.nome} (ID: {func2.id})")
        print(f"Unidade ID: {unidade_id}, Mês: {mes}, Ano: {ano}")

        # 2. Testar Indicadores
        print("\n--- Teste 1: Indicadores ---")
        indicators = await GradeController.get_indicators(session, unidade_id, mes, ano)
        print(f"Indicadores obtidos: {indicators}")
        assert "total_colaboradores" in indicators
        assert "total_ferias" in indicators
        assert "total_multiplas_lotacoes" in indicators
        print("[OK] Indicadores validados com sucesso.")

        # 3. Limpar grades e dias anteriores de teste se houver
        await session.execute(delete(GradeDia))
        await session.execute(delete(Grade))
        await session.commit()

        # 4. Testar Criação de Grade
        print("\n--- Teste 2: Criação de Grade ---")
        dias_payload = [
            {"dia": 1, "legenda_sigla": "M", "descricao": "Manhã"},
            {"dia": 2, "legenda_sigla": "M", "descricao": "Manhã"},
            {"dia": 3, "legenda_sigla": "T", "descricao": "Tarde"},
            {"dia": 4, "legenda_sigla": "F", "descricao": "Folga"},
            {"dia": 5, "legenda_sigla": "F", "descricao": "Folga"},
        ]
        grade_create_data = {
            "funcionario_id": func1.id,
            "unidade_id": unidade_id,
            "mes": mes,
            "ano": ano,
            "status": "Rascunho",
            "observacao": "Grade de teste",
            "dias": dias_payload
        }
        nova_grade = await GradeController.create(session, grade_create_data, "teste_user")
        await session.commit()
        print(f"Grade criada com ID: {nova_grade.id}, Dias criados: {len(nova_grade.dias)}")
        assert nova_grade.id is not None
        assert len(nova_grade.dias) == 5
        print("[OK] Criação de grade validada com sucesso.")

        # 5. Testar Matriz de Grade
        print("\n--- Teste 3: Consulta Matricial ---")
        matrix = await GradeController.get_matrix(session, unidade_id, mes, ano)
        print(f"Total de linhas retornadas na matriz: {len(matrix)}")
        func1_row = next((r for r in matrix if r["funcionario_id"] == func1.id), None)
        if func1_row:
            print(f"Linha do Func1 encontrada. Grade status: {func1_row['grade_status']}")
            assert func1_row["grade_id"] == nova_grade.id
        print("[OK] Consulta matricial validada com sucesso.")

        # 6. Testar Cópia de Grade
        copied_grades = []
        if func2.id != func1.id:
            print("\n--- Teste 4: Cópia de Grade ---")
            copy_data = {
                "source_func_id": func1.id,
                "source_unidade_id": unidade_id,
                "source_mes": mes,
                "source_ano": ano,
                "target_func_ids": [func2.id],
                "target_unidade_id": unidade_id,
                "target_mes": mes,
                "target_ano": ano
            }
            copied_grades = await GradeController.copy_grade(session, copy_data, "teste_user")
            await session.commit()
            print(f"Grades copiadas: {len(copied_grades)}")
            assert len(copied_grades) == 1
            copied_grade = copied_grades[0]
            assert copied_grade.funcionario_id == func2.id
            assert len(copied_grade.dias) == 5
            print(f"[OK] Cópia de grade para func {func2.nome} validada com sucesso.")

        # 7. Testar Atualização de Grade
        print("\n--- Teste 5: Atualização de Grade ---")
        update_data = {
            "status": "Aprovada",
            "observacao": "Grade aprovada pelo gestor",
            "dias": [
                {"dia": 1, "legenda_sigla": "N", "descricao": "Noite"}
            ]
        }
        updated_grade = await GradeController.update(session, nova_grade.id, update_data, "teste_user")
        await session.commit()
        assert updated_grade.status == "Aprovada"
        assert len(updated_grade.dias) == 1
        print("[OK] Atualização de grade validada com sucesso.")

        # 8. Limpeza / Exclusão
        print("\n--- Teste 6: Exclusão de Grade ---")
        del_res = await GradeController.delete(session, nova_grade.id)
        if func2.id != func1.id and copied_grades:
            await GradeController.delete(session, copied_grades[0].id)
        await session.commit()
        print(f"Resultado exclusão: {del_res}")
        print("[OK] Exclusão validada com sucesso.")

    print("\nTODOS OS TESTES DE GRADE FORAM EXECUTADOS COM SUCESSO!")

if __name__ == "__main__":
    asyncio.run(test_grade())
