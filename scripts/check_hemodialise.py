import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import select
from src.resources.database import DatabaseManager
from src.models.uorg import Uorg
from src.models.posto import Posto
from src.models.funcionario import Funcionario

matriculas_alvo = [
    "3048008", "2164828", "2173683", "2232181", "2241712",
    "3433437", "2232211", "2173775", "2244744", "3319587",
    "3507182", "3467618", "1864400", "3312362", "3422267",
    "3507458", "3139447", "1507288", "2232733", "3250019"
]

async def check_data():
    db_url = os.getenv("APP_DB_URL") or os.getenv("SQLITE_DSN") or "sqlite+aiosqlite:///app.db"
    db_manager = DatabaseManager(db_url)
    
    async for session in db_manager.get_session():
        # 1. Procurar UORG
        res_uorgs = await session.execute(select(Uorg))
        uorgs = res_uorgs.scalars().all()
        print("--- UORGS ENCONTRADAS ---")
        for u in uorgs:
            if "urin" in u.nome.lower() or "hemo" in u.nome.lower() or "nefro" in u.nome.lower():
                print(f"UORG ID: {u.id} | Código: {u.codigo} | Sigla: {u.sigla} | Nome: {u.nome}")

        # 2. Procurar Postos
        res_postos = await session.execute(select(Posto))
        postos = res_postos.scalars().all()
        print("\n--- POSTOS ENCONTRADOS ---")
        for p in postos:
            if "hemo" in p.nome.lower() or "urin" in p.nome.lower() or "dial" in p.nome.lower():
                print(f"POSTO ID: {p.id} | Nome: {p.nome} | UORG_ID: {p.uorg_id} | Unidade_ID: {p.unidade_id}")

        # 3. Procurar os Funcionários por Matrícula
        print("\n--- FUNCIONÁRIOS ---")
        stmt_f = select(Funcionario).where(Funcionario.matricula.in_(matriculas_alvo))
        res_f = await session.execute(stmt_f)
        funcs = res_f.scalars().all()
        funcs_map = {f.matricula: f for f in funcs}
        for m in matriculas_alvo:
            if m in funcs_map:
                f = funcs_map[m]
                print(f"Achou: {m} - {f.nome} (ID: {f.id})")
            else:
                print(f"NÃO ACHOU: {m}")
        break

if __name__ == "__main__":
    asyncio.run(check_data())
