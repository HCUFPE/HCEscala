from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.resources.database import Base

class Posto(Base):
    __tablename__ = "postos"
    __table_args__ = (
        UniqueConstraint("nome", "uorg_id", name="uq_postos_nome_uorg_id"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(200), nullable=False)
    uorg_id = Column(Integer, ForeignKey("uorgs.id", ondelete="CASCADE"), nullable=True, index=True)
    unidade_id = Column(Integer, nullable=True)
    
    # Auditoria
    login = Column(String(100), nullable=False)
    data_alteracao = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    uorg = relationship("Uorg", back_populates="postos")

