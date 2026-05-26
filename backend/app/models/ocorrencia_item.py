from sqlalchemy import Column, Identity, Integer, String, Numeric, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class OcorrenciaItem(Base):
    __tablename__ = "ocorrencia_itens"

    id = Column(Integer, Identity(always=False), primary_key=True)
    ocorrencia_id = Column(Integer, ForeignKey("ocorrencias.id"), nullable=False, index=True)

    codprod = Column(String(20))
    descricao_produto = Column(String(200))
    qtd_afetada = Column(Numeric(15, 3))
    valor_unitario = Column(Numeric(15, 2))
    valor_total = Column(Numeric(15, 2))
    item_role = Column(String(30), nullable=False, default="AFETADO")

    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    ocorrencia = relationship("Ocorrencia", back_populates="itens")
