from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.resources.database import Base

class Setor(Base):
    __tablename__ = "setores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String, unique=True, index=True, nullable=False)
    
    # Auditoria
    login = Column(String, nullable=False)
    data_alteracao = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    unidades = relationship("Unidade", back_populates="setor", cascade="all, delete-orphan")
