from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_gerente_user, get_write_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioUpdate
from app.services.user_service import user_service

router = APIRouter(prefix="/users", tags=["Usuários"])


@router.post("/", response_model=UsuarioResponse, status_code=201)
def create_user(
    data: UsuarioCreate,
    db: Session = Depends(get_write_db),
    _: Usuario = Depends(get_gerente_user),
):
    return user_service.create_user(db, data)


@router.get("/", response_model=List[UsuarioResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_write_db),
    _: Usuario = Depends(get_gerente_user),
):
    return user_service.get_all_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UsuarioResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_write_db),
    _: Usuario = Depends(get_gerente_user),
):
    return user_service.get_user_by_id(db, user_id)


@router.put("/{user_id}", response_model=UsuarioResponse)
def update_user(
    user_id: int,
    data: UsuarioUpdate,
    db: Session = Depends(get_write_db),
    _: Usuario = Depends(get_gerente_user),
):
    return user_service.update_user(db, user_id, data)
