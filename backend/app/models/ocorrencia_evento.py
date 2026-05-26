from sqlalchemy import Column, Identity, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class OcorrenciaEvento(Base):
    __tablename__ = "ocorrencia_eventos"

    id = Column(Integer, Identity(always=False), primary_key=True)
    ocorrencia_id = Column(Integer, ForeignKey("ocorrencias.id"), nullable=False)

    tipo_evento = Column(String(30), nullable=False)
    status_anterior = Column(String(30))
    status_novo = Column(String(30))
    comentario = Column(String(2000))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    ocorrencia = relationship("Ocorrencia", back_populates="eventos")
    usuario = relationship("Usuario", foreign_keys=[usuario_id])
