"""
Modelo SQLAlchemy de Auditoria e Trilha de Mudanças (Audit Log)
================================================================
Registra de forma estruturada e imutável as ações de mutação (criação, alteração, exclusão,
troca de privilégios) realizadas por usuários no sistema.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from ..resources.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario = Column(String(100), nullable=False, index=True)
    tela = Column(String(100), nullable=False, index=True)
    tabela = Column(String(100), nullable=False, index=True)
    operacao = Column(String(20), nullable=False, index=True)  # INSERT, UPDATE, DELETE, REVERT
    registro_id = Column(String(50), nullable=False, index=True)
    dados_anteriores = Column(Text, nullable=True)             # JSON serializado do estado BEFORE (dados_anteriores)
    dados_posteriores = Column(Text, nullable=True)            # JSON serializado do estado AFTER (dados_novos)
    data_hora = Column(DateTime, default=datetime.now, nullable=False, index=True)
    revertido = Column(Boolean, default=False, nullable=False)
    revertido_por = Column(String(100), nullable=True)
    revertido_em = Column(DateTime, nullable=True)

    # Propriedades de compatibilidade com o padrão SETISD (categoria, acao, recurso, dados_novos)
    @property
    def categoria(self) -> str:
        return self.tela

    @property
    def acao(self) -> str:
        return self.operacao

    @property
    def recurso(self) -> str:
        return f"{self.tabela}:{self.registro_id}"

    @property
    def dados_novos(self):
        return self.dados_posteriores

    def __repr__(self):
        return f"<AuditLog id={self.id} usuario={self.usuario} operacao={self.operacao} tabela={self.tabela}:{self.registro_id}>"
