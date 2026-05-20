from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.core.database import read_engine
from app.models.usuario import Usuario
from app.schemas.carregamento import NotaFiscalEnvelope
from app.services.carregamento_service import carregamento_service

router = APIRouter(prefix="/notas-fiscais", tags=["Notas Fiscais"])


@router.get("/{numnota}", response_model=NotaFiscalEnvelope)
def get_nota_fiscal(
    numnota: int,
    _: Usuario = Depends(get_current_user),
):
    data = carregamento_service.get_por_nota(read_engine, numnota)
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota fiscal não encontrada.",
        )
    return data
