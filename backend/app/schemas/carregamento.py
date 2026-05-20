from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class ProdutoSchema(BaseModel):
    codprod: int
    qt: float
    pvenda: float


class NotaFiscalResponse(BaseModel):
    numero_nota: int
    data_faturamento: Optional[date]
    cliente: Optional[str]
    valor_total: Optional[float]
    vendedor: Optional[str]
    id_carregamento: Optional[int]
    data_saida_carregamento: Optional[date]
    motorista: Optional[str]
    produtos: List[ProdutoSchema]


class NotaFiscalEnvelope(BaseModel):
    nota_fiscal: NotaFiscalResponse
