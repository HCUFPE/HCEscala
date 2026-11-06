import asyncio
import sys
import os

# Adiciona o diretório raiz ao sys.path para conseguir importar de src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import select

from src.resources.database import DatabaseManager
from src.models.cargo import Cargo
from src.models.vinculo import Vinculo

async def process_data(file_path: str):
    if not os.path.exists(file_path):
        print(f"Erro: O arquivo '{file_path}' não foi encontrado.")
        return

    vinculos_unicos = set()
    cargos_unicos = set()

    print("Lendo o arquivo...")
    with open(file_path, 'r', encoding='utf-8') as f:
        # Pular cabeçalho
        next(f, None)
        
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                vinculo_nome = parts[0].strip()
                cargo_nome = parts[3].strip()
                
                if vinculo_nome:
                    vinculos_unicos.add(vinculo_nome)
                if cargo_nome:
                    cargos_unicos.add(cargo_nome)

    print(f"Encontrados {len(vinculos_unicos)} vínculos distintos e {len(cargos_unicos)} cargos distintos no arquivo.")
    print("Iniciando gravação no banco de dados...")

    db_manager = DatabaseManager("sqlite+aiosqlite:///app.db")
    
    async for session in db_manager.get_session():
        # ----- Processar Vínculos -----
        vinculos_adicionados = 0
        for nome in vinculos_unicos:
            stmt = select(Vinculo).where(Vinculo.nome == nome)
            result = await session.execute(stmt)
            if not result.scalars().first():
                novo_vinculo = Vinculo(nome=nome, login="script_carga")
                session.add(novo_vinculo)
                vinculos_adicionados += 1
        
        # ----- Processar Cargos -----
        cargos_adicionados = 0
        for nome in cargos_unicos:
            stmt = select(Cargo).where(Cargo.nome == nome)
            result = await session.execute(stmt)
            if not result.scalars().first():
                # Como a carga horária não vem na planilha, vamos usar 40 como padrão. 
                # Pode ser alterado depois pela interface.
                novo_cargo = Cargo(nome=nome, carga_horaria=40, login="script_carga")
                session.add(novo_cargo)
                cargos_adicionados += 1
                
        await session.commit()
        
        print(f"Sucesso! Foram adicionados {vinculos_adicionados} novos vínculos.")
        print(f"Sucesso! Foram adicionados {cargos_adicionados} novos cargos (Carga Horária padrão: 40h).")


if __name__ == "__main__":
    arquivo = "dados_rh.tsv"
    asyncio.run(process_data(arquivo))
