from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_write_db
from app.models.usuario import Usuario
from app.web.session import load_token


class RequiresLogin(Exception):
    pass


class RequiresGerente(Exception):
    pass


async def get_current_web_user(request: Request, db: Session = Depends(get_write_db)) -> Usuario:
    token = request.cookies.get("gsac_session")
    if not token:
        raise RequiresLogin()
    data = load_token(token)
    if not data:
        raise RequiresLogin()
    user = db.query(Usuario).filter(Usuario.id == data["user_id"], Usuario.ativo == 1).first()
    if not user:
        raise RequiresLogin()
    return user


async def require_gerente(current_user: Usuario = Depends(get_current_web_user)) -> Usuario:
    from app.utils.enums import RoleEnum
    if current_user.papel != RoleEnum.GERENTE:
        raise RequiresGerente()
    return current_user
