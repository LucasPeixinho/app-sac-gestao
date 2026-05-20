import os
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.anexo import Anexo

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"


def _ocorrencia_dir(ocorrencia_id: int) -> Path:
    path = UPLOAD_DIR / "ocorrencias" / str(ocorrencia_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


class AnexoService:

    @staticmethod
    async def save(db: Session, ocorrencia_id: int, file: UploadFile, current_user) -> Anexo:
        ext = Path(file.filename).suffix
        nome_unico = f"{uuid.uuid4().hex}{ext}"
        destino = _ocorrencia_dir(ocorrencia_id) / nome_unico

        contents = await file.read()
        with open(destino, "wb") as f:
            f.write(contents)

        anexo = Anexo(
            ocorrencia_id=ocorrencia_id,
            nome_arquivo=file.filename,
            caminho_arquivo=str(destino),
            mime_type=file.content_type,
            tamanho=len(contents),
            criado_por_id=current_user.id,
        )
        db.add(anexo)
        db.commit()
        db.refresh(anexo)
        return anexo

    @staticmethod
    def delete(db: Session, anexo_id: int, current_user) -> None:
        from app.utils.enums import RoleEnum

        anexo = db.query(Anexo).filter(Anexo.id == anexo_id).first()
        if not anexo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anexo não encontrado.")

        if current_user.papel == RoleEnum.OPERADOR and anexo.criado_por_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado.")

        if os.path.exists(anexo.caminho_arquivo):
            os.remove(anexo.caminho_arquivo)

        db.delete(anexo)
        db.commit()

    @staticmethod
    def get_file_path(db: Session, anexo_id: int, current_user) -> tuple[str, str]:
        from app.utils.enums import RoleEnum

        anexo = db.query(Anexo).filter(Anexo.id == anexo_id).first()
        if not anexo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anexo não encontrado.")

        if current_user.papel == RoleEnum.OPERADOR and anexo.criado_por_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado.")

        if not os.path.exists(anexo.caminho_arquivo):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo não encontrado no servidor.")

        return anexo.caminho_arquivo, anexo.nome_arquivo


anexo_service = AnexoService()
