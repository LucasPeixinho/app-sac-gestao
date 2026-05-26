from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.database import get_write_db
from app.models.ocorrencia import Ocorrencia
from app.models.usuario import Usuario
from app.utils.enums import RoleEnum
from app.web.dependencies import get_current_web_user
from app.web.templates_config import templates

router = APIRouter(tags=["web-dashboard"])


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def dashboard_home(
    request: Request,
    current_user: Usuario = Depends(get_current_web_user),
    db: Session = Depends(get_write_db),
):
    query = db.query(Ocorrencia)
    if current_user.papel == RoleEnum.OPERADOR:
        query = query.filter(Ocorrencia.atribuido_a_id == current_user.id)

    todas = query.all()
    total = len(todas)
    em_tratamento = sum(1 for o in todas if o.status == "EM_TRATAMENTO")
    finalizado = sum(1 for o in todas if o.status == "FINALIZADO")
    concluido = sum(1 for o in todas if o.status == "CONCLUIDO")

    recentes_q = db.query(Ocorrencia)
    if current_user.papel == RoleEnum.OPERADOR:
        recentes_q = recentes_q.filter(Ocorrencia.atribuido_a_id == current_user.id)
    recentes = recentes_q.order_by(Ocorrencia.created_at.desc()).limit(5).all()

    return templates.TemplateResponse(
        request,
        "pages/dashboard/home.html",
        {
            "current_user": current_user,
            "page_title": "Dashboard",
            "total": total,
            "em_tratamento": em_tratamento,
            "finalizado": finalizado,
            "concluido": concluido,
            "recentes": recentes,
        },
    )
