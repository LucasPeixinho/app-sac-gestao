from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel

from app.utils.enums import SituacaoOcorrenciaEnum


class AnexoResponse(BaseModel):
    id: int
    nome_arquivo: str
    mime_type: Optional[str]
    tamanho: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class OcorrenciaCreate(BaseModel):
    numero_nota_fiscal: int
    situacao: SituacaoOcorrenciaEnum
    motivo: Optional[str] = None
    observacoes: Optional[str] = None
    encaminhamento: Optional[str] = None


class OcorrenciaUpdate(BaseModel):
    situacao: Optional[SituacaoOcorrenciaEnum] = None
    motivo: Optional[str] = None
    observacoes: Optional[str] = None
    encaminhamento: Optional[str] = None


class OcorrenciaResponse(BaseModel):
    id: int
    numero_nota_fiscal: str
    id_carregamento: Optional[int]
    data_faturamento: Optional[date]
    data_saida_carregamento: Optional[date]
    cliente: Optional[str]
    motorista: Optional[str]
    vendedor: Optional[str]
    valor_total: Optional[float]
    situacao: str
    motivo: Optional[str]
    observacoes: Optional[str]
    encaminhamento: Optional[str]
    status: str
    criado_por_id: int
    criado_por_nome: Optional[str]
    aprovado_por_id: Optional[int]
    aprovado_por_nome: Optional[str]
    aprovado_em: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    anexos: List[AnexoResponse] = []

    class Config:
        from_attributes = True
