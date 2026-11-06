from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.resources.database import Base

class UsuarioGerencia(Base):
    """
    Representa a delegação de gerência/chefia concedida a um usuário sobre um nível
    organizacional (DIVGP_ADMIN, UORG ou POSTO).
    """
    __tablename__ = "usuario_gerencias"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario = Column(String(100), index=True, nullable=False) # Login / Matrícula / Username AD
    nome = Column(String(200), nullable=False) # Nome do Gestor
    nivel = Column(String(50), nullable=False) # DIVGP_ADMIN, UORG, POSTO
    
    uorg_id = Column(Integer, ForeignKey("uorgs.id"), nullable=True, index=True)
    posto_id = Column(Integer, ForeignKey("postos.id"), nullable=True, index=True)
    
    ativo = Column(Boolean, default=True, nullable=False)

    # Auditoria
    login = Column(String(100), nullable=False)
    data_alteracao = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    uorg = relationship("Uorg")
    posto = relationship("Posto")

    # Alias de compatibilidade
    @property
    def unidade(self):
        return self.uorg

    @property
    def setor(self):
        return self.uorg
