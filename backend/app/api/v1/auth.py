from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_write_db
from app.core.security import create_access_token
from app.schemas.auth import Token
from app.services.user_service import user_service

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_write_db),
):
    user = user_service.authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.ativo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário inativo.")

    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token, token_type="bearer")
