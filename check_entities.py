import asyncio
from sqlalchemy import text
from src.resources.database import get_db

async def check_info():
    async for db in get_db():
        uorgs = (await db.execute(text("SELECT id, nome, sigla FROM uorgs WHERE LOWER(nome) LIKE '%ambulat%'"))).mappings().all()
        print("UORGS:", uorgs)
        postos = (await db.execute(text("SELECT id, nome, uorg_id FROM postos WHERE LOWER(nome) LIKE '%oncol%'"))).mappings().all()
        print("POSTOS:", postos)
        break

if __name__ == "__main__":
    asyncio.run(check_info())
