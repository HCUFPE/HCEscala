from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.resources.database import Base

class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    funcionario_id = Column(Integer, ForeignKey("funcionarios.id"), nullable=False, index=True)
    uorg_id = Column(Integer, ForeignKey("uorgs.id"), nullable=False, index=True)
    posto_id = Column(Integer, ForeignKey("postos.id"), nullable=True)
    mes = Column(Integer, nullable=False)  # 1 a 12
    ano = Column(Integer, nullable=False)  # ex: 2026
    status = Column(String(50), default="Rascunho", nullable=False)
    observacao = Column(String(500), nullable=True)

    # Auditoria
    login = Column(String(100), nullable=False)
    data_alteracao = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    funcionario = relationship("Funcionario")
    uorg = relationship("Uorg")
    posto = relationship("Posto")
    dias = relationship("GradeDia", back_populates="grade", cascade="all, delete-orphan", order_by="GradeDia.dia")

    # Alias de compatibilidade
    @property
    def unidade(self):
        return self.uorg

    @property
    def unidade_id(self):
        return self.uorg_id

    __table_args__ = (
        UniqueConstraint("funcionario_id", "uorg_id", "mes", "ano", name="uq_grade_func_uorg_mes_ano"),
    )


class GradeDia(Base):
    __tablename__ = "grade_dias"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    grade_id = Column(Integer, ForeignKey("grades.id", ondelete="CASCADE"), nullable=False, index=True)
    dia = Column(Integer, nullable=False)  # 1 a 31
    escala_id = Column(Integer, ForeignKey("escalas.id"), nullable=True)
    legenda_sigla = Column(String(20), nullable=True)  # ex: 'M', 'T', 'N', 'FE', 'F', 'SN', 'D'
    descricao = Column(String(100), nullable=True)

    # Relacionamentos
    grade = relationship("Grade", back_populates="dias")
    escala = relationship("Escala")

    __table_args__ = (
        UniqueConstraint("grade_id", "dia", name="uq_grade_dia"),
    )
