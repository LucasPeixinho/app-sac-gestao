"""Instância única de Jinja2Templates compartilhada pelos routers web."""
from datetime import datetime

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="../frontend/templates")
templates.env.globals["now"] = datetime.utcnow
