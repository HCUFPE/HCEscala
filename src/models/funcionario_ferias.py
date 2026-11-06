from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.resources.database import Base

class FuncionarioFerias(Base):
    __tablename__ = "funcionarios_ferias"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    funcionario_id = Column(Integer, ForeignKey("funcionarios.id"), nullable=False)
    
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)

    # Auditoria
    login = Column(String(100), nullable=False)
    data_alteracao = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    funcionario = relationship("Funcionario", back_populates="ferias")
