from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_write_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.services.user_service import user_service
from app.utils.enums import RoleEnum
from app.web.dependencies import get_current_web_user

router = APIRouter(prefix="/usuarios", tags=["web-usuarios"])
templates = Jinja2Templates(directory="app/templates")


def _check_gerente(current_user: Usuario):
    if current_user.papel != RoleEnum.GERENTE:
        raise PermissionError()


@router.get("", response_class=HTMLResponse, include_in_schema=False)
async def list_usuarios(
    request: Request,
    current_user: Usuario = Depends(get_current_web_user),
    db: Session = Depends(get_write_db),
):
    try:
        _check_gerente(current_user)
    except PermissionError:
        return RedirectResponse(url="/", status_code=302)

    usuarios = user_service.get_all_users(db)
    sucesso = request.query_params.get("sucesso", "")
    return templates.TemplateResponse(
        request,
        "pages/usuarios/list.html",
        {"current_user": current_user, "page_title": "Usuários", "usuarios": usuarios, "sucesso": sucesso},
    )


@router.get("/novo", response_class=HTMLResponse, include_in_schema=False)
async def create_usuario_page(
    request: Request,
    current_user: Usuario = Depends(get_current_web_user),
):
    try:
        _check_gerente(current_user)
    except PermissionError:
        return RedirectResponse(url="/", status_code=302)

    return templates.TemplateResponse(
        request,
        "pages/usuarios/create.html",
        {
            "current_user": current_user,
            "page_title": "Novo Usuário",
            "papeis": RoleEnum,
            "erro": request.query_params.get("erro", ""),
        },
    )


@router.post("", include_in_schema=False)
async def create_usuario(
    current_user: Usuario = Depends(get_current_web_user),
    db: Session = Depends(get_write_db),
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    papel: str = Form(...),
):
    try:
        _check_gerente(current_user)
    except PermissionError:
        return RedirectResponse(url="/", status_code=302)

    try:
        user_service.create_user(db, UsuarioCreate(nome=nome, email=email, senha=senha, papel=RoleEnum(papel)))
        return RedirectResponse(url="/usuarios?sucesso=Usuário+criado+com+sucesso", status_code=302)
    except Exception as e:
        return RedirectResponse(url=f"/usuarios/novo?erro={str(e)}", status_code=302)


@router.get("/{usuario_id}/editar", response_class=HTMLResponse, include_in_schema=False)
async def edit_usuario_page(
    usuario_id: int,
    request: Request,
    current_user: Usuario = Depends(get_current_web_user),
    db: Session = Depends(get_write_db),
):
    try:
        _check_gerente(current_user)
    except PermissionError:
        return RedirectResponse(url="/", status_code=302)

    try:
        usuario = user_service.get_user_by_id(db, usuario_id)
    except Exception:
        return RedirectResponse(url="/usuarios", status_code=302)

    return templates.TemplateResponse(
        request,
        "pages/usuarios/edit.html",
        {
            "current_user": current_user,
            "page_title": f"Editar — {usuario.nome}",
            "usuario": usuario,
            "papeis": RoleEnum,
            "erro": request.query_params.get("erro", ""),
        },
    )


@router.post("/{usuario_id}/atualizar", include_in_schema=False)
async def update_usuario(
    usuario_id: int,
    current_user: Usuario = Depends(get_current_web_user),
    db: Session = Depends(get_write_db),
    nome: str = Form(...),
    email: str = Form(...),
    senha: Optional[str] = Form(None),
    papel: str = Form(...),
    ativo: Optional[str] = Form(None),
):
    try:
        _check_gerente(current_user)
    except PermissionError:
        return RedirectResponse(url="/", status_code=302)

    try:
        data = UsuarioUpdate(
            nome=nome, email=email,
            senha=senha if senha else None,
            papel=RoleEnum(papel),
            ativo=ativo == "on",
        )
        user_service.update_user(db, usuario_id, data)
        return RedirectResponse(url="/usuarios?sucesso=Usuário+atualizado+com+sucesso", status_code=302)
    except Exception as e:
        return RedirectResponse(url=f"/usuarios/{usuario_id}/editar?erro={str(e)}", status_code=302)
