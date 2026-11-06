import asyncio
import os
import sys
from datetime import datetime, time
from dotenv import load_dotenv

# Adiciona o diretório raiz ao sys.path para conseguir importar src.resources
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.models.escala import Escala
from sqlalchemy.future import select

load_dotenv()

# Dados extraídos da tabela com a flag `apenas_assistenciais` inferida pelos cabeçalhos
ESCALAS_DATA = [
    # 4 HORAS - Todas as categorias
    ("06:00", "10:00", "644", "M19", False),
    ("06:30", "10:30", "645", "M20", False),
    ("07:00", "11:00", "902", "M8", False),
    ("07:30", "11:30", "646", "M21", False),
    ("08:00", "12:00", "904", "M10", False),
    ("08:30", "12:30", "647", "M22", False),
    ("09:00", "13:00", "905", "M11", False),
    ("09:30", "13:30", "648", "M23", False),
    ("10:00", "14:00", "906", "M12", False),
    ("10:30", "14:30", "649", "M24", False),
    ("11:00", "15:00", "650", "M25", False),
    ("11:30", "15:30", "651", "M26", False),
    ("12:00", "16:00", "901", "T9", False),
    ("12:30", "16:30", "652", "T20", False),
    ("13:00", "17:00", "907", "T10", False),
    ("13:30", "17:30", "653", "T21", False),
    ("14:00", "18:00", "908", "T11", False),
    ("14:30", "18:30", "654", "T22", False),
    ("15:00", "19:00", "909", "T12", False),
    ("15:30", "19:30", "655", "T23", False),
    ("16:00", "20:00", "656", "T24", False),
    # 4 HORAS - Assistencial
    ("16:30", "20:30", "677", "T25", True),
    ("17:00", "21:00", "678", "T26", True),
    ("17:30", "21:30", "679", "T27", True),
    ("18:00", "22:00", "900", "N11", True),
    
    # 5 HORAS
    ("06:00", "11:15", "705", "JOR12", False),
    ("06:30", "11:45", "709", "JOR14", False),
    ("07:00", "12:15", "508", "JOR1", False),
    ("07:30", "12:45", "711", "JOR15", False),
    ("08:00", "13:15", "509", "JOR2", False),
    ("08:30", "13:45", "706", "JOR16", False),
    ("09:00", "14:15", "641", "JOR6", False),
    ("09:30", "14:45", "672", "JOR17", False),
    ("10:00", "15:15", "642", "JOR7", False),
    ("10:30", "15:45", "673", "JOR18", False),
    ("11:00", "16:15", "643", "JOR8", False),
    ("11:30", "16:45", "674", "JOR19", False),
    ("12:00", "17:15", "510", "JOR3", False),
    ("12:30", "17:45", "675", "JOR20", False),
    ("13:00", "18:15", "511", "JOR4", False),
    ("13:30", "18:45", "676", "JOR21", False),
    ("14:00", "19:15", "512", "JOR5", False),
    ("14:30", "19:45", "693", "JOR22", False),
    
    # 6 HORAS - Todas categorias
    ("06:00", "12:15", "514", "M13", False),
    ("06:30", "12:45", "516", "M14", False),
    ("07:00", "13:15", "518", "M15", False),
    ("07:30", "13:45", "520", "M16", False),
    ("08:00", "14:15", "522", "M17", False),
    ("08:30", "14:45", "657", "M27", False),
    ("09:00", "15:15", "658", "M28", False),
    ("09:30", "15:45", "659", "M29", False),
    ("10:00", "16:15", "524", "M18", False),
    ("10:30", "16:45", "660", "M30", False),
    ("11:00", "17:15", "661", "M31", False),
    ("11:30", "17:45", "662", "M32", False),
    ("12:00", "18:15", "527", "T13", False),
    ("12:30", "18:45", "529", "T14", False),
    ("13:00", "19:15", "531", "T15", False),
    ("13:30", "19:45", "533", "T16", False),
    # 6 HORAS - Assistencial
    ("14:00", "20:15", "535", "T17", True),
    ("14:30", "20:45", "663", "T28", True),
    ("15:00", "21:15", "537", "T18", True),
    ("15:30", "21:45", "539", "T19", True),
    
    # 7 HORAS (30 min int)
    ("06:00", "13:30", "682", "JOR23", False),
    ("06:30", "14:00", "683", "JOR25", False),
    ("07:00", "14:30", "632", "JOR9", False),
    ("07:30", "15:00", "633", "JOR10", False),
    ("08:00", "15:30", "634", "JOR11", False),
    ("08:30", "16:00", "635", "JOR12_2", False), # Conflito sigla JOR12 anterior (cód 705) -> JOR12_2
    ("09:00", "16:30", "684", "JOR26", False),
    ("09:30", "17:00", "685", "JOR27", False),
    ("10:00", "17:30", "686", "JOR28", False),
    ("10:30", "18:00", "687", "JOR29", False),
    ("11:00", "18:30", "637", "JOR17_2", False),
    ("11:30", "19:00", "688", "JOR30", False),
    ("12:00", "19:30", "689", "JOR31", False),
    ("12:30", "20:00", "690", "JOR32", False),
    
    # 7 HORAS (1h int)
    ("06:00", "14:00", "691", "JOR33", False),
    ("06:30", "14:30", "692", "JOR34", False),
    ("07:00", "15:00", "716", "JOR21_2", False),
    ("08:00", "16:00", "694", "JOR35", False),
    ("09:00", "17:00", "695", "JOR36", False),
    ("10:00", "18:00", "636", "JOR24", False),
    ("11:00", "19:00", "696", "JOR37", False),
    ("12:00", "20:00", "697", "JOR38", False),
    
    # 7 HORAS (2h int)
    ("06:00", "15:00", "737", "JOR40", False),
    ("06:30", "15:30", "738", "JOR41", False),
    ("07:00", "16:00", "739", "JOR42", False),
    ("08:00", "17:00", "740", "JOR43", False),
    ("09:00", "18:00", "741", "JOR44", False),
    ("10:00", "19:00", "742", "JOR45", False),
    ("11:00", "20:00", "743", "JOR46", False),
    
    # 8 HORAS (30 min int) - Todas categorias
    ("06:00", "14:30", "638", "MT13", False),
    ("06:30", "15:00", "639", "MT14", False),
    ("07:00", "15:30", "541", "MT15", False),
    ("07:30", "16:00", "542", "MT16", False),
    ("08:00", "16:30", "543", "MT17", False),
    ("08:30", "17:00", "544", "MT18", False),
    ("09:00", "17:30", "545", "MT19", False),
    ("09:30", "18:00", "546", "MT20", False),
    ("10:00", "18:30", "547", "MT21", False),
    ("10:30", "19:00", "548", "MT22", False),
    ("11:00", "19:30", "549", "MT23", False),
    ("11:30", "20:00", "640", "MT44", False),
    # 8 HORAS (30 min int) - Assistencial
    ("12:00", "20:30", "666", "TN2", True),
    ("12:30", "21:00", "667", "TN3", True),
    ("13:00", "21:30", "668", "TN4", True),
    ("13:30", "22:00", "676", "TN7", True), # Cód 676 repete? 
    
    # 8 HORAS (1h int) - Todas
    ("06:00", "15:00", "550", "MT24", False),
    ("06:30", "15:30", "626", "MT25", False),
    ("07:00", "16:00", "552", "MT26", False),
    ("07:30", "16:30", "554", "MT27", False),
    ("08:00", "17:00", "556", "MT28", False),
    ("08:30", "17:30", "558", "MT29", False),
    ("09:00", "18:00", "560", "MT30", False),
    ("09:30", "18:30", "562", "MT31", False),
    ("10:00", "19:00", "564", "MT32", False),
    ("10:30", "19:30", "566", "MT33", False),
    ("11:00", "20:00", "568", "MT34", False),
    # 8 HORAS (1h int) - Assistencial
    ("11:30", "20:30", "669", "MT47", True),
    ("12:00", "21:00", "670", "TN5", True),
    ("12:30", "21:30", "671", "TN6", True),
    ("13:00", "22:00", "617", "TN1", True),
    
    # 8 HORAS (2h int) - Todas
    ("06:00", "16:00", "664", "MT45", False),
    ("06:30", "16:30", "665", "MT46", False),
    ("07:00", "17:00", "570", "MT36", False),
    ("07:30", "17:30", "572", "MT37", False),
    ("08:00", "18:00", "574", "MT38", False),
    ("08:30", "18:30", "576", "MT39", False),
    ("09:00", "19:00", "578", "MT40", False),
    ("09:30", "19:30", "580", "MT41", False),
    ("10:00", "20:00", "582", "MT42", False),
    # 8 HORAS (2h int) - Assistencial
    ("10:30", "20:30", "583", "MT43", True),
    ("11:00", "21:00", "673_2", "MT48", True), # Cód 673 repetido (JOR18) -> "673_2"
    ("11:30", "21:30", "674_2", "MT49", True), # Cód 674 repetido (JOR19)
    ("12:00", "22:00", "675_2", "TN8", True),  # Cód 675 repetido (JOR20)
    
    # PLANTÕES 12 HORAS DIURNO
    ("06:00", "18:00", "584", "D5", False),
    ("06:30", "18:30", "623", "D11", False),
    ("07:00", "19:00", "586", "D6", False),
    ("07:30", "19:30", "588", "D7", False),
    ("08:00", "20:00", "590", "D8", False),
    ("08:30", "20:30", "680", "D12", False),
    ("09:00", "21:00", "619", "D9", False),
    ("09:30", "21:30", "681", "D13", False),
    ("10:00", "22:00", "621", "D10", False),
    
    # PLANTÕES 12 HORAS NOTURNO
    ("18:00", "06:00", "592", "N6", False),
    ("18:30", "06:30", "594", "N7", False),
    ("19:00", "07:00", "596", "N8", False),
    ("19:30", "07:30", "598", "N9", False),
    ("20:00", "08:00", "600", "N10", False),
    
    # PLANTÕES 24 HORAS
    ("06:00", "06:00", "602", "DN4", False),
    ("07:00", "07:00", "603", "DN5", False),
    ("08:00", "08:00", "604", "DN6", False)
]

def str_to_time(time_str):
    h, m = time_str.split(':')
    return time(int(h), int(m))

async def seed():
    app_dsn = os.getenv("SQLITE_DSN")
    if not app_dsn:
        print("SQLITE_DSN not found.")
        return
        
    engine = create_async_engine(app_dsn, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        for inicio, fim, codigo, sigla, apenas_assistenciais in ESCALAS_DATA:
            # Check if exists
            result = await session.execute(select(Escala).where(Escala.codigo == codigo))
            if not result.scalars().first():
                escala = Escala(
                    inicio_jornada=str_to_time(inicio),
                    fim_jornada=str_to_time(fim),
                    codigo=codigo,
                    sigla=sigla,
                    apenas_assistenciais=apenas_assistenciais,
                    login="sistema_seed"
                )
                session.add(escala)
        
        await session.commit()
        print(f"{len(ESCALAS_DATA)} escalas avaliadas e cadastradas no banco de dados!")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed())
