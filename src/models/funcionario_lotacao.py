from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.resources.database import Base

class FuncionarioLotacao(Base):
    __tablename__ = "funcionarios_lotacoes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    funcionario_id = Column(Integer, ForeignKey("funcionarios.id"), nullable=False)
    uorg_id = Column(Integer, ForeignKey("uorgs.id"), nullable=True, index=True)
    posto_id = Column(Integer, ForeignKey("postos.id"), nullable=True, index=True)
    
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=True)

    # Auditoria
    login = Column(String(100), nullable=False)
    data_alteracao = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    funcionario = relationship("Funcionario", back_populates="lotacoes")
    uorg = relationship("Uorg")
    posto = relationship("Posto")

    # Alias de compatibilidade
    @property
    def unidade(self):
        return self.uorg

    @property
    def unidade_id(self):
        return self.uorg_id
