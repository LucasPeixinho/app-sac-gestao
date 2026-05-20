from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate


class UserService:

    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> Optional[Usuario]:
        user = db.query(Usuario).filter(Usuario.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.senha_hash):
            return None
        return user

    @staticmethod
    def create_user(db: Session, data: UsuarioCreate) -> Usuario:
        existing = db.query(Usuario).filter(Usuario.email == data.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="E-mail já cadastrado.",
            )
        user = Usuario(
            nome=data.nome,
            email=data.email,
            senha_hash=get_password_hash(data.senha),
            papel=data.papel.value,
            ativo=1,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[Usuario]:
        return db.query(Usuario).offset(skip).limit(limit).all()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Usuario:
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
        return user

    @staticmethod
    def update_user(db: Session, user_id: int, data: UsuarioUpdate) -> Usuario:
        user = UserService.get_user_by_id(db, user_id)

        if data.email is not None:
            conflict = db.query(Usuario).filter(Usuario.email == data.email, Usuario.id != user_id).first()
            if conflict:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail já cadastrado.")
            user.email = data.email

        if data.nome is not None:
            user.nome = data.nome
        if data.senha is not None:
            user.senha_hash = get_password_hash(data.senha)
        if data.papel is not None:
            user.papel = data.papel.value
        if data.ativo is not None:
            user.ativo = 1 if data.ativo else 0

        db.commit()
        db.refresh(user)
        return user


user_service = UserService()
