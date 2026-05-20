from typing import Optional

from fastapi import APIRouter, Depends, Form, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_write_db, read_engine
from app.models.usuario import Usuario
from app.schemas.ocorrencia import OcorrenciaCreate, OcorrenciaUpdate
from app.services.anexo_service import anexo_service
from app.services.carregamento_service import carregamento_service
from app.services.ocorrencia_service import ocorrencia_service
from app.utils.enums import RoleEnum, SituacaoOcorrenciaEnum, StatusOcorrenciaEnum
from app.web.dependencies import get_current_web_user

router = APIRouter(prefix="/ocorrencias", tags=["web-ocorrencias"])
templates = Jinja2Templates(directory="app/templates")

SITUACAO_LABELS = {
    "DEVOLUCAO_TOTAL": "Devolução Total",
    "DEVOLUCAO_PARCIAL": "Devolução Parcial",
    "INVERSAO_MERCADORIA": "Inversão de Mercadoria",
    "SOBRA": "Sobra",
    "AVARIA": "Avaria",
    "COLETA": "Coleta",
}


@router.get("", response_class=HTMLResponse, include_in_schema=False)
async def list_ocorrencias(
    request: Request,
    current_user: Usuario = Depends(get_current_web_user),
    db: Session = Depends(get_write_db),
    status: Optional[str] = None,
    situacao: Optional[str] = None,
    numero_nota_fiscal: Optional[str] = None,
):
    ocorrencias = ocorrencia_service.list(
        db, current_user,
        status_filter=status or None,
        situacao=situacao or None,
        numero_nota_fiscal=numero_nota_fiscal or None,
    )
    return templates.TemplateResponse(
        request,
        "pages/ocorrencias/list.html",
        {
            "current_user": current_user,
            "page_title": "Ocorrências",
            "ocorrencias": ocorrencias,
            "status_filter": status or "",
            "situacao_filter": situacao or "",
            "nota_filter": numero_nota_fiscal or "",
            "situacoes": SituacaoOcorrenciaEnum,
            "status_enum": StatusOcorrenciaEnum,
            "situacao_labels": SITUACAO_LABELS,
        },
    )


@router.get("/nova", response_class=HTMLResponse, include_in_schema=False)
async def create_ocorrencia_page(
    request: Request,
    current_user: Usuario = Depends(get_current_web_user),
):
    return templates.TemplateResponse(
        request,
        "pages/ocorrencias/create.html",
        {
            "current_user": current_user,
            "page_title": "Nova Ocorrência",
            "situacoes": SituacaoOcorrenciaEnum,
            "situacao_labels": SITUACAO_LABELS,
            "erro": request.query_params.get("erro", ""),
        },
    )


@router.get("/buscar-nota", response_class=HTMLResponse, include_in_schema=False)
async def buscar_nota(
    request: Request,
    current_user: Usuario = Depends(get_current_web_user),
    numero_nota_fiscal: Optional[str] = None,
):
    nota = None
    erro = None
    if numero_nota_fiscal:
        try:
            resultado = carregamento_service.get_por_nota(read_engine, int(numero_nota_fiscal))
            if resultado:
                nota = resultado["nota_fiscal"]
            else:
                erro = "Nota fiscal não encontrada no CEDEP."
        except ValueError:
            erro = "Número de nota inválido."
        except Exception as e:
            erro = f"Erro ao consultar nota: {str(e)}"
    else:
        erro = "Informe o número da nota fiscal."

    return templates.TemplateResponse(request, "partials/nota_info.html", {"nota": nota, "erro": erro})


@router.post("", include_in_schema=False)
async def create_ocorrencia(
    request: Request,
    current_user: Usuario = Depends(get_current_web_user),
    db: Session = Depends(get_write_db),
    numero_nota_fiscal: str = Form(...),
    situacao: str = Form(...),
    motivo: Optional[str] = Form(None),
    observacoes: Optional[str] = Form(None),
    encaminhamento: Optional[str] = Form(None),
):
    try:
        data = OcorrenciaCreate(
            numero_nota_fiscal=int(numero_nota_fiscal),
            situacao=SituacaoOcorrenciaEnum(situacao),
            motivo=motivo or None,
            observacoes=observacoes or None,
            encaminhamento=encaminhamento or None,
        )
        result = ocorrencia_service.create(db, data, current_user)
        return RedirectResponse(url=f"/ocorrencias/{result['id']}", status_code=302)
    except Exception as e:
        msg = str(e)
        erro = "Nota fiscal não encontrada no CEDEP." if "não encontrada" in msg.lower() else f"Erro: {msg}"
        return RedirectResponse(url=f"/ocorrencias/nova?erro={erro}", status_code=302)


@router.get("/{ocorrencia_id}", response_class=HTMLResponse, include_in_schema=False)
async def view_ocorrencia(
    ocorrencia_id: int,
    request: Request,
    current_user: Usuario = Depends(get_current_web_user),
    db: Session = Depends(get_write_db),
):
    try:
        ocorrencia = ocorrencia_service.get(db, ocorrencia_id, current_user)
    except Exception:
        return RedirectResponse(url="/ocorrencias", status_code=302)

    return templates.TemplateResponse(
        request,
        "pages/ocorrencias/view.html",
        {
            "current_user": current_user,
            "page_title": f"Ocorrência #{ocorrencia_id}",
            "ocorrencia": ocorrencia,
            "situacao_labels": SITUACAO_LABELS,
            "sucesso": request.query_params.get("sucesso", ""),
            "erro": request.query_params.get("erro", ""),
        },
    )


@router.get("/{ocorrencia_id}/editar", response_class=HTMLResponse, include_in_schema=False)
async def edit_ocorrencia_page(
    ocorrencia_id: int,
    request: Request,
    current_user: Usuario = Depends(get_current_web_user),
    db: Session = Depends(get_write_db),
):
    try:
        ocorrencia = ocorrencia_service.get(db, ocorrencia_id, current_user)
    except Exception:
        return RedirectResponse(url="/ocorrencias", status_code=302)

    if ocorrencia["status"] == "FINALIZADO":
        return RedirectResponse(url=f"/ocorrencias/{ocorrencia_id}?erro=Ocorrência+finalizada", status_code=302)

    return templates.TemplateResponse(
        request,
        "pages/ocorrencias/edit.html",
        {
            "current_user": current_user,
            "page_title": f"Editar Ocorrência #{ocorrencia_id}",
            "ocorrencia": ocorrencia,
            "situacoes": SituacaoOcorrenciaEnum,
            "situacao_labels": SITUACAO_LABELS,
            "erro": request.query_params.get("erro", ""),
        },
    )


@router.post("/{ocorrencia_id}/atualizar", include_in_schema=False)
async def update_ocorrencia(
    ocorrencia_id: int,
    current_user: Usuario = Depends(get_current_web_user),
    db: Session = Depends(get_write_db),
    situacao: Optional[str] = Form(None),
    motivo: Optional[str] = Form(None),
    observacoes: Optional[str] = Form(None),
    encaminhamento: Optional[str] = Form(None),
):
    try:
        data = OcorrenciaUpdate(
            situacao=SituacaoOcorrenciaEnum(situacao) if situacao else None,
            motivo=motivo or None,
            observacoes=observacoes or None,
            encaminhamento=encaminhamento or None,
        )
        ocorrencia_service.update(db, ocorrencia_id, data, current_user)
        return RedirectResponse(url=f"/ocorrencias/{ocorrencia_id}?sucesso=Ocorrência+atualizada", status_code=302)
    except Exception as e:
        return RedirectResponse(url=f"/ocorrencias/{ocorrencia_id}/editar?erro={str(e)}", status_code=302)


@router.post("/{ocorrencia_id}/anexos", include_in_schema=False)
async def upload_anexo(
    ocorrencia_id: int,
    current_user: Usuario = Depends(get_current_web_user),
    db: Session = Depends(get_write_db),
    file: UploadFile = File(...),
):
    try:
        ocorrencia_service.get(db, ocorrencia_id, current_user)
        await anexo_service.save(db, ocorrencia_id, file, current_user)
        return RedirectResponse(url=f"/ocorrencias/{ocorrencia_id}?sucesso=Anexo+adicionado", status_code=302)
    except Exception as e:
        return RedirectResponse(url=f"/ocorrencias/{ocorrencia_id}?erro={str(e)}", status_code=302)


@router.post("/{ocorrencia_id}/anexos/{anexo_id}/deletar", include_in_schema=False)
async def delete_anexo(
    ocorrencia_id: int,
    anexo_id: int,
    current_user: Usuario = Depends(get_current_web_user),
    db: Session = Depends(get_write_db),
):
    try:
        anexo_service.delete(db, anexo_id, current_user)
        return RedirectResponse(url=f"/ocorrencias/{ocorrencia_id}?sucesso=Anexo+removido", status_code=302)
    except Exception as e:
        return RedirectResponse(url=f"/ocorrencias/{ocorrencia_id}?erro={str(e)}", status_code=302)
