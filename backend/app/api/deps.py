from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_read_db, get_write_db
from app.core.permissions import require_gerente
from app.core.security import decode_access_token
from app.models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_write_db),
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    if not user.ativo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário inativo.")

    return user


def get_gerente_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    require_gerente(current_user)
    return current_user
