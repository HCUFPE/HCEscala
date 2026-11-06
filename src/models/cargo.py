from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..resources.database import Base

class Cargo(Base):
    __tablename__ = "cargos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(100), unique=True, index=True, nullable=False)
    login = Column(String(100), nullable=False)
    data_alteracao = Column(DateTime, server_default=func.now(), onupdate=func.now())
