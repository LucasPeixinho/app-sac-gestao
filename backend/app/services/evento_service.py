from sqlalchemy.orm import Session

from app.models.ocorrencia_evento import OcorrenciaEvento


class EventoService:

    @staticmethod
    def registrar_evento(
        db: Session,
        ocorrencia_id: int,
        tipo_evento: str,
        status_anterior: str | None,
        status_novo: str | None,
        comentario: str | None,
        usuario_id: int,
    ) -> OcorrenciaEvento:
        evt = OcorrenciaEvento(
            ocorrencia_id=ocorrencia_id,
            tipo_evento=tipo_evento,
            status_anterior=status_anterior,
            status_novo=status_novo,
            comentario=comentario,
            usuario_id=usuario_id,
        )
        db.add(evt)
        db.flush()
        return evt

    @staticmethod
    def registrar_mudanca_status(
        db: Session,
        ocorrencia_id: int,
        anterior: str,
        novo: str,
        comentario: str | None,
        usuario_id: int,
    ) -> OcorrenciaEvento:
        return EventoService.registrar_evento(
            db, ocorrencia_id, "MUDANCA_STATUS", anterior, novo, comentario, usuario_id
        )

    @staticmethod
    def listar(db: Session, ocorrencia_id: int) -> list[OcorrenciaEvento]:
        return (
            db.query(OcorrenciaEvento)
            .filter(OcorrenciaEvento.ocorrencia_id == ocorrencia_id)
            .order_by(OcorrenciaEvento.created_at.asc())
            .all()
        )


evento_service = EventoService()
