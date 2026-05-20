from sqlalchemy import Column, Identity, Integer, String, Numeric, Date, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Ocorrencia(Base):
    __tablename__ = "ocorrencias"

    id = Column(Integer, Identity(always=False), primary_key=True)

    # Nota fiscal
    numero_nota_fiscal = Column(String(50), nullable=False, index=True)

    # Snapshot do CEDEP no momento da criação
    id_carregamento = Column(Integer)
    data_faturamento = Column(Date)
    data_saida_carregamento = Column(Date)
    cliente = Column(String(200))
    motorista = Column(String(200))
    vendedor = Column(String(200))
    valor_total = Column(Numeric(15, 2))

    # Dados da ocorrência
    situacao = Column(String(50), nullable=False)
    motivo = Column(String(1000))
    observacoes = Column(String(2000))
    encaminhamento = Column(String(2000))

    # Status
    status = Column(String(20), nullable=False, default="NOVO")

    # Relacionamentos
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    aprovado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    aprovado_em = Column(TIMESTAMP)

    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    criado_por = relationship("Usuario", foreign_keys=[criado_por_id])
    aprovado_por = relationship("Usuario", foreign_keys=[aprovado_por_id])
    anexos = relationship("Anexo", back_populates="ocorrencia", cascade="all, delete-orphan")
