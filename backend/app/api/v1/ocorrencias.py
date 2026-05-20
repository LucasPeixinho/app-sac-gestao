from typing import List, Optional

from fastapi import APIRouter, Depends, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_write_db
from app.models.usuario import Usuario
from app.schemas.ocorrencia import OcorrenciaCreate, OcorrenciaResponse, OcorrenciaUpdate, AnexoResponse
from app.services.ocorrencia_service import ocorrencia_service
from app.services.anexo_service import anexo_service

router = APIRouter(prefix="/ocorrencias", tags=["Ocorrências"])


@router.post("/", response_model=OcorrenciaResponse, status_code=status.HTTP_201_CREATED)
def create_ocorrencia(
    data: OcorrenciaCreate,
    db: Session = Depends(get_write_db),
    current_user: Usuario = Depends(get_current_user),
):
    return ocorrencia_service.create(db, data, current_user)


@router.get("/", response_model=List[OcorrenciaResponse])
def list_ocorrencias(
    status_filter: Optional[str] = None,
    situacao: Optional[str] = None,
    numero_nota_fiscal: Optional[str] = None,
    db: Session = Depends(get_write_db),
    current_user: Usuario = Depends(get_current_user),
):
    return ocorrencia_service.list(db, current_user, status_filter, situacao, numero_nota_fiscal)


@router.get("/{ocorrencia_id}", response_model=OcorrenciaResponse)
def get_ocorrencia(
    ocorrencia_id: int,
    db: Session = Depends(get_write_db),
    current_user: Usuario = Depends(get_current_user),
):
    return ocorrencia_service.get(db, ocorrencia_id, current_user)


@router.put("/{ocorrencia_id}", response_model=OcorrenciaResponse)
def update_ocorrencia(
    ocorrencia_id: int,
    data: OcorrenciaUpdate,
    db: Session = Depends(get_write_db),
    current_user: Usuario = Depends(get_current_user),
):
    return ocorrencia_service.update(db, ocorrencia_id, data, current_user)


@router.post("/{ocorrencia_id}/anexos", response_model=AnexoResponse, status_code=status.HTTP_201_CREATED)
async def upload_anexo(
    ocorrencia_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_write_db),
    current_user: Usuario = Depends(get_current_user),
):
    # Verifica se a ocorrência existe e o usuário tem acesso
    ocorrencia_service.get(db, ocorrencia_id, current_user)
    anexo = await anexo_service.save(db, ocorrencia_id, file, current_user)
    return {
        "id": anexo.id,
        "nome_arquivo": anexo.nome_arquivo,
        "mime_type": anexo.mime_type,
        "tamanho": anexo.tamanho,
        "created_at": anexo.created_at,
    }


@router.get("/{ocorrencia_id}/anexos/{anexo_id}/download")
def download_anexo(
    ocorrencia_id: int,
    anexo_id: int,
    db: Session = Depends(get_write_db),
    current_user: Usuario = Depends(get_current_user),
):
    caminho, nome = anexo_service.get_file_path(db, anexo_id, current_user)
    return FileResponse(path=caminho, filename=nome)


@router.delete("/{ocorrencia_id}/anexos/{anexo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_anexo(
    ocorrencia_id: int,
    anexo_id: int,
    db: Session = Depends(get_write_db),
    current_user: Usuario = Depends(get_current_user),
):
    anexo_service.delete(db, anexo_id, current_user)
