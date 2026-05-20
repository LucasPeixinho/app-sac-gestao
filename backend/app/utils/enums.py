from enum import Enum


class RoleEnum(str, Enum):
    OPERADOR = "OPERADOR"
    GERENTE = "GERENTE"


class SituacaoOcorrenciaEnum(str, Enum):
    DEVOLUCAO_TOTAL = "DEVOLUCAO_TOTAL"
    DEVOLUCAO_PARCIAL = "DEVOLUCAO_PARCIAL"
    INVERSAO_MERCADORIA = "INVERSAO_MERCADORIA"
    SOBRA = "SOBRA"
    AVARIA = "AVARIA"
    COLETA = "COLETA"


class StatusOcorrenciaEnum(str, Enum):
    NOVO = "NOVO"
    ENCAMINHADO = "ENCAMINHADO"
    FINALIZADO = "FINALIZADO"
