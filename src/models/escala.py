from sqlalchemy import Column, Integer, String, Boolean, DateTime, Time
from sqlalchemy.sql import func
from ..resources.database import Base

class Escala(Base):
    __tablename__ = "escalas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    inicio_jornada = Column(Time, nullable=False)
    fim_jornada = Column(Time, nullable=False)
    codigo = Column(String(50), nullable=True, default="")
    sigla = Column(String(20), unique=True, index=True, nullable=False)
    descricao = Column(String(255), nullable=True, default="")
    apenas_assistenciais = Column(Boolean, default=False, nullable=False)
    login = Column(String(100), nullable=False)
    data_alteracao = Column(DateTime, server_default=func.now(), onupdate=func.now())
