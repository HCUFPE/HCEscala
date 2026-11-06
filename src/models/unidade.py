from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.resources.database import Base

class Unidade(Base):
    __tablename__ = "unidades"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String, unique=True, index=True, nullable=False)
    setor_id = Column(Integer, ForeignKey("setores.id"), nullable=True)
    
    # Auditoria
    login = Column(String, nullable=False)
    data_alteracao = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    setor = relationship("Setor", back_populates="unidades")
