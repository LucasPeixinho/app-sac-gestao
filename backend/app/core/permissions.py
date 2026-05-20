from fastapi import HTTPException, status

from app.utils.enums import RoleEnum


def require_gerente(user) -> None:
    if user.papel != RoleEnum.GERENTE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a gerentes.",
        )
