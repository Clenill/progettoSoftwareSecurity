from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db 
from app.core.security import get_current_user
from app.db.models import User

from app.db.database import get_db

ui_router = APIRouter()

# Configurazione Jinja2
BASE_PATH = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_PATH / "templates"))

@ui_router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Pagina di login"""
    return templates.TemplateResponse(request=request, name="login.html")

@ui_router.get("/dashboard/utente", response_class=HTMLResponse)
async def dashboard_paziente(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard_paziente.html")

@ui_router.get("/dashboard/staff", response_class=HTMLResponse)
async def dashboard_medico(request: Request):
    """Area riservata al Medico"""
    return templates.TemplateResponse(request=request, name="dashboard_medico.html")

@ui_router.get("/dashboard/admin", response_class=HTMLResponse)
async def dashboard_authority(request: Request):
    """Area riservata all'Autorità di Controllo"""
    return templates.TemplateResponse(request=request, name="dashboard_authority.html")