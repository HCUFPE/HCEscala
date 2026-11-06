from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.resources.database import Base

class Funcionario(Base):
    __tablename__ = "funcionarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    matricula = Column(String(50), unique=True, index=True, nullable=False)
    nome = Column(String(200), nullable=False)
    carga_horaria = Column(Integer, nullable=False, default=40)
    cargo_id = Column(Integer, ForeignKey("cargos.id"), nullable=False)
    escala_id = Column(Integer, ForeignKey("escalas.id"), nullable=False)
    vinculo_id = Column(Integer, ForeignKey("vinculos.id"), nullable=True)

    # Auditoria
    login = Column(String(100), nullable=False)
    data_alteracao = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamentos Principais
    cargo = relationship("Cargo")
    escala = relationship("Escala")
    vinculo = relationship("Vinculo")

    # Relacionamentos Filhos
    lotacoes = relationship("FuncionarioLotacao", back_populates="funcionario", cascade="all, delete-orphan")
    ferias = relationship("FuncionarioFerias", back_populates="funcionario", cascade="all, delete-orphan")
