import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from src.resources.database import DatabaseManager
from src.controllers.feriado_controller import FeriadoController
import os
from dotenv import load_dotenv

load_dotenv()

async def seed_feriados():
    db_url = os.getenv("APP_DB_URL") or os.getenv("SQLITE_DSN") or "sqlite+aiosqlite:///app.db"
    db_manager = DatabaseManager(db_url)
    
    feriados = [
        {"data": date(2026, 1, 1), "nome": "Confraternização Universal", "tipo": "Feriado Nacional"},
        {"data": date(2026, 1, 2), "nome": "Ponto facultativo", "tipo": "Ponto Facultativo"},
        {"data": date(2026, 2, 16), "nome": "Carnaval", "tipo": "Ponto Facultativo"},
        {"data": date(2026, 2, 17), "nome": "Carnaval", "tipo": "Ponto Facultativo"},
        {"data": date(2026, 2, 18), "nome": "Quarta-feira de Cinzas", "tipo": "Ponto Facultativo até as 14:00"},
        {"data": date(2026, 3, 6), "nome": "Data Magna de Pernambuco", "tipo": "Feriado Estadual"},
        {"data": date(2026, 4, 3), "nome": "Paixão de Cristo", "tipo": "Feriado Nacional"},
        {"data": date(2026, 4, 20), "nome": "Ponto facultativo", "tipo": "Ponto Facultativo"},
        {"data": date(2026, 4, 21), "nome": "Tiradentes", "tipo": "Feriado Nacional"},
        {"data": date(2026, 5, 1), "nome": "Dia Mundial do Trabalho", "tipo": "Feriado Nacional"},
        {"data": date(2026, 6, 4), "nome": "Corpus Christi", "tipo": "Ponto Facultativo"},
        {"data": date(2026, 6, 5), "nome": "Ponto facultativo", "tipo": "Ponto Facultativo"},
        {"data": date(2026, 6, 24), "nome": "São João", "tipo": "Feriado Estadual"},
        {"data": date(2026, 7, 16), "nome": "Nossa Senhora do Carmo", "tipo": "Feriado Municipal"},
        {"data": date(2026, 9, 7), "nome": "Independência do Brasil", "tipo": "Feriado Nacional"},
        {"data": date(2026, 10, 12), "nome": "Nossa Senhora Aparecida", "tipo": "Feriado Nacional"},
        {"data": date(2026, 10, 28), "nome": "Dia do Servidor Público", "tipo": "Ponto Facultativo"},
        {"data": date(2026, 11, 2), "nome": "Finados", "tipo": "Feriado Nacional"},
        {"data": date(2026, 11, 15), "nome": "Proclamação da República", "tipo": "Feriado Nacional"},
        {"data": date(2026, 11, 20), "nome": "Dia Nacional de Zumbi e da Consciência Negra", "tipo": "Feriado Nacional"},
        {"data": date(2026, 12, 8), "nome": "Nossa Senhora da Conceição", "tipo": "Feriado Municipal"},
        {"data": date(2026, 12, 24), "nome": "Véspera do Natal", "tipo": "Ponto Facultativo após as 13 horas"},
        {"data": date(2026, 12, 25), "nome": "Natal", "tipo": "Feriado Nacional"},
        {"data": date(2026, 12, 31), "nome": "Véspera do Ano Novo", "tipo": "Ponto Facultativo após as 13 horas"}
    ]

    async for session in db_manager.get_session():
        for f in feriados:
            try:
                print(f"Cadastrando {f['nome']} ({f['data']})...")
                # Avoid duplicate insertion check by directly catching exceptions or check existence
                await FeriadoController.create(session, f, "system")
            except Exception as e:
                print(f"Erro ao cadastrar {f['nome']}: {e}")
                await session.rollback()
        
        break # Only need one session

if __name__ == "__main__":
    asyncio.run(seed_feriados())
