from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..resources.database import Base

class Legenda(Base):
    __tablename__ = "legendas"

    id = Column(Integer, primary_key=True, index=True)
    sigla = Column(String(10), unique=True, index=True, nullable=False)
    descricao = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
