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

@ui_router.get("/registrazione", response_class=HTMLResponse)
async def register_page(request: Request):
    """Pagina di registrazione"""
    return templates.TemplateResponse(request=request, name="registrazione.html")

@ui_router.get("/dashboard/utente", response_class=HTMLResponse)
async def dashboard_paziente(request: Request):
    return templates.TemplateResponse(request=request, name="home_paziente.html")

@ui_router.get("/utente/prenota", response_class=HTMLResponse)
async def prenota_page(request: Request):
    """Pagina per effettuare una prenotazione"""
    return templates.TemplateResponse(request=request, name="dashboard_paziente.html")

@ui_router.get("/utente/visite", response_class=HTMLResponse)
async def visualizza_visite_page(request: Request):
    """Pagina per visualizzare gli appuntamenti"""
    return templates.TemplateResponse(request=request, name="visite_paziente.html")

@ui_router.get("/dashboard/staff", response_class=HTMLResponse)
async def dashboard_medico(request: Request):
    """Area riservata al Medico"""
    return templates.TemplateResponse(request=request, name="dashboard_medico.html")

@ui_router.get("/dettagli-visita", response_class=HTMLResponse)
async def dettagli_visita_page(request: Request):
    """Pagina di dettaglio della singola visita per il Medico"""
    return templates.TemplateResponse(request=request, name="dettagli_visita.html")

@ui_router.get("/dashboard/admin", response_class=HTMLResponse)
async def dashboard_admin(request: Request):
    """Area riservata all'Autorità di Controllo"""
    return templates.TemplateResponse(request=request, name="dashboard_admin.html")

@ui_router.get("/dashboard/authority", response_class=HTMLResponse)
async def dashboard_authority(request: Request):
    """Area riservata all'Autorità di Controllo"""
    return templates.TemplateResponse(request=request, name="dashboard_authority.html")