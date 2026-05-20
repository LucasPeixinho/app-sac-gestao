from sqlalchemy import Column, Identity, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Anexo(Base):
    __tablename__ = "anexos"

    id = Column(Integer, Identity(always=False), primary_key=True)
    ocorrencia_id = Column(Integer, ForeignKey("ocorrencias.id"), nullable=False, index=True)
    nome_arquivo = Column(String(255), nullable=False)
    caminho_arquivo = Column(String(500), nullable=False)
    mime_type = Column(String(100))
    tamanho = Column(Integer)
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    ocorrencia = relationship("Ocorrencia", back_populates="anexos")
    criado_por = relationship("Usuario", foreign_keys=[criado_por_id])
