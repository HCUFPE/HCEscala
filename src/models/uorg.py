from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.resources.database import Base

class Uorg(Base):
    """
    Representa uma Unidade Organizacional (UORG) na estrutura hierárquica do hospital.
    Substitui e unifica os antigos conceitos de Setor e Unidade, permitindo níveis
    hierárquicos flexíveis através do auto-relacionamento uorg_pai_id.
    """
    __tablename__ = "uorgs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(50), nullable=True, index=True)
    sigla = Column(String(50), nullable=True, index=True)
    nome = Column(String(200), unique=True, index=True, nullable=False)
    uorg_pai_id = Column(Integer, ForeignKey("uorgs.id", ondelete="SET NULL"), nullable=True, index=True)

    # Auditoria
    login = Column(String(100), nullable=False)
    data_alteracao = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    uorg_pai = relationship("Uorg", remote_side=[id], back_populates="subordinadas")
    subordinadas = relationship("Uorg", back_populates="uorg_pai")
    postos = relationship("Posto", back_populates="uorg", cascade="all, delete-orphan")
