from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import read_engine
from app.models.ocorrencia import Ocorrencia
from app.schemas.ocorrencia import OcorrenciaCreate, OcorrenciaResponse, OcorrenciaUpdate
from app.services.carregamento_service import carregamento_service


def _to_response(o: Ocorrencia) -> dict:
    return {
        "id": o.id,
        "numero_nota_fiscal": o.numero_nota_fiscal,
        "id_carregamento": o.id_carregamento,
        "data_faturamento": o.data_faturamento,
        "data_saida_carregamento": o.data_saida_carregamento,
        "cliente": o.cliente,
        "motorista": o.motorista,
        "vendedor": o.vendedor,
        "valor_total": float(o.valor_total) if o.valor_total is not None else None,
        "situacao": o.situacao,
        "motivo": o.motivo,
        "observacoes": o.observacoes,
        "encaminhamento": o.encaminhamento,
        "status": o.status,
        "criado_por_id": o.criado_por_id,
        "criado_por_nome": o.criado_por.nome if o.criado_por else None,
        "aprovado_por_id": o.aprovado_por_id,
        "aprovado_por_nome": o.aprovado_por.nome if o.aprovado_por else None,
        "aprovado_em": o.aprovado_em,
        "created_at": o.created_at,
        "updated_at": o.updated_at,
        "anexos": [
            {
                "id": a.id,
                "nome_arquivo": a.nome_arquivo,
                "mime_type": a.mime_type,
                "tamanho": a.tamanho,
                "created_at": a.created_at,
            }
            for a in (o.anexos or [])
        ],
    }


def _load(db: Session, ocorrencia_id: int) -> Ocorrencia:
    o = (
        db.query(Ocorrencia)
        .options(
            joinedload(Ocorrencia.criado_por),
            joinedload(Ocorrencia.aprovado_por),
            joinedload(Ocorrencia.anexos),
        )
        .filter(Ocorrencia.id == ocorrencia_id)
        .first()
    )
    if not o:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ocorrência não encontrada.")
    return o


class OcorrenciaService:

    @staticmethod
    def create(db: Session, data: OcorrenciaCreate, current_user) -> dict:
        nota = carregamento_service.get_por_nota(read_engine, data.numero_nota_fiscal)
        if nota is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nota fiscal não encontrada no CEDEP.",
            )

        nf = nota["nota_fiscal"]

        o = Ocorrencia(
            numero_nota_fiscal=str(data.numero_nota_fiscal),
            id_carregamento=nf.get("id_carregamento"),
            data_faturamento=nf.get("data_faturamento"),
            data_saida_carregamento=nf.get("data_saida_carregamento"),
            cliente=nf.get("cliente"),
            motorista=nf.get("motorista"),
            vendedor=nf.get("vendedor"),
            valor_total=nf.get("valor_total"),
            situacao=data.situacao.value,
            motivo=data.motivo,
            observacoes=data.observacoes,
            encaminhamento=data.encaminhamento,
            status="NOVO",
            criado_por_id=current_user.id,
        )
        db.add(o)
        db.commit()

        return _to_response(_load(db, o.id))

    @staticmethod
    def list(
        db: Session,
        current_user,
        status_filter: Optional[str] = None,
        situacao: Optional[str] = None,
        numero_nota_fiscal: Optional[str] = None,
    ) -> List[dict]:
        from app.utils.enums import RoleEnum

        query = db.query(Ocorrencia).options(
            joinedload(Ocorrencia.criado_por),
            joinedload(Ocorrencia.aprovado_por),
            joinedload(Ocorrencia.anexos),
        )

        if current_user.papel == RoleEnum.OPERADOR:
            query = query.filter(Ocorrencia.criado_por_id == current_user.id)

        if status_filter:
            query = query.filter(Ocorrencia.status == status_filter)
        if situacao:
            query = query.filter(Ocorrencia.situacao == situacao)
        if numero_nota_fiscal:
            query = query.filter(Ocorrencia.numero_nota_fiscal == numero_nota_fiscal)

        return [_to_response(o) for o in query.order_by(Ocorrencia.created_at.desc()).all()]

    @staticmethod
    def get(db: Session, ocorrencia_id: int, current_user) -> dict:
        from app.utils.enums import RoleEnum

        o = _load(db, ocorrencia_id)

        if current_user.papel == RoleEnum.OPERADOR and o.criado_por_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado.")

        return _to_response(o)

    @staticmethod
    def update(db: Session, ocorrencia_id: int, data: OcorrenciaUpdate, current_user) -> dict:
        from app.utils.enums import RoleEnum

        o = _load(db, ocorrencia_id)

        if current_user.papel == RoleEnum.OPERADOR and o.criado_por_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado.")

        if o.status == "FINALIZADO":
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Ocorrência finalizada não pode ser alterada.")

        if data.situacao is not None:
            o.situacao = data.situacao.value
        if data.motivo is not None:
            o.motivo = data.motivo
        if data.observacoes is not None:
            o.observacoes = data.observacoes
        if data.encaminhamento is not None and current_user.papel == RoleEnum.GERENTE:
            o.encaminhamento = data.encaminhamento

        db.commit()
        return _to_response(_load(db, o.id))


ocorrencia_service = OcorrenciaService()
