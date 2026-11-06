from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.sql import func
from src.resources.database import Base

class Feriado(Base):
    __tablename__ = "feriados"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String, nullable=False, index=True)
    data = Column(Date, nullable=False, index=True)
    tipo = Column(String, nullable=False) # Nacional, Estadual, Municipal, Institucional
    
    # Auditoria
    login = Column(String, nullable=False)
    data_alteracao = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
