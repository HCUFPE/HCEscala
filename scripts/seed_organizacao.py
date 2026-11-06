import asyncio
import sys
import os

# Adiciona o diretório raiz ao sys.path para conseguir importar de src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from src.resources.database import DatabaseManager
from src.models.setor import Setor
from src.models.unidade import Unidade
from src.models.posto import Posto

async def process_data(file_path: str):
    if not os.path.exists(file_path):
        print(f"Erro: O arquivo '{file_path}' não foi encontrado.")
        return

    locais_unicos = set()

    print("Lendo o arquivo...")
    with open(file_path, 'r', encoding='utf-8') as f:
        # Pular cabeçalho
        next(f, None)
        
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 5:
                lotacao = parts[4].strip()
                if lotacao:
                    locais_unicos.add(lotacao)

    # Classificando
    nomes_setores = []
    nomes_unidades = []

    for local in locais_unicos:
        upper_local = local.upper()
        if upper_local.startswith("SETOR ") or upper_local.startswith("DIVISAO ") or upper_local.startswith("GERENCIA "):
            nomes_setores.append(local)
        else:
            nomes_unidades.append(local)

    print(f"Encontrados {len(nomes_setores)} setores/divisões e {len(nomes_unidades)} unidades.")
    print("Iniciando gravação no banco de dados...")

    db_manager = DatabaseManager("sqlite+aiosqlite:///app.db")
    
    # Criar tabelas caso não existam
    from src.resources.database import Base
    async with db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async for session in db_manager.get_session():
        login_script = "script_carga_org"
        
        # 1. Garantir que exista um Setor "GERAL" para atrelar as unidades órfãs
        stmt_geral = select(Setor).where(Setor.nome == "SETOR GERAL (PADRÃO)")
        result = await session.execute(stmt_geral)
        setor_geral = result.scalars().first()
        
        if not setor_geral:
            setor_geral = Setor(nome="SETOR GERAL (PADRÃO)", login=login_script)
            session.add(setor_geral)
            await session.flush()
        
        setores_adicionados = 0
        unidades_adicionadas = 0

        # ----- Processar Setores -----
        for nome in nomes_setores:
            stmt = select(Setor).where(Setor.nome == nome)
            result = await session.execute(stmt)
            if not result.scalars().first():
                novo_setor = Setor(nome=nome, login=login_script)
                session.add(novo_setor)
                setores_adicionados += 1
                
        # ----- Processar Unidades -----
        for nome in nomes_unidades:
            stmt = select(Unidade).where(Unidade.nome == nome)
            result = await session.execute(stmt)
            if not result.scalars().first():
                nova_unidade = Unidade(nome=nome, setor_id=setor_geral.id, login=login_script)
                session.add(nova_unidade)
                unidades_adicionadas += 1
                
        await session.commit()
        
        print(f"Sucesso! Foram adicionados {setores_adicionados} novos setores.")
        print(f"Sucesso! Foram adicionadas {unidades_adicionadas} novas unidades (atreladas ao Setor Geral).")


if __name__ == "__main__":
    arquivo = "dados_rh.tsv"
    asyncio.run(process_data(arquivo))
