from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.core.security import has_role_in, get_current_user_or_none
from app.db.models import User
from app.enum.ruolo import ruolo
from uuid import UUID

ui_router = APIRouter()

# Configurazione Jinja2
BASE_PATH = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_PATH / "templates"))

@ui_router.get("/", response_class=HTMLResponse)
async def login_page(request: Request, current_user: User | None = Depends(get_current_user_or_none)):
    """Pagina di login"""
    if current_user == None:
        return templates.TemplateResponse(request=request, name="login.html")
    
    if current_user.ruolo == ruolo.PAZIENTE:
        return RedirectResponse("/dashboard/utente")
    elif current_user.ruolo == ruolo.AUTORITY:
        return RedirectResponse("/dashboard/authority")
    elif current_user.ruolo == ruolo.MEDICO:
        return RedirectResponse("/dashboard/staff")


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
async def dashboard_admin(request: Request, current_user: User = Depends(has_role_in([ruolo.AUTORITY]))):
    """Area riservata all'Autorità di Controllo"""
    return templates.TemplateResponse(request=request, name="dashboard_admin.html")

@ui_router.get("/dashboard/authority", response_class=HTMLResponse)
async def dashboard_authority(request: Request, current_user: User = Depends(has_role_in([ruolo.AUTORITY]))):
    """Area riservata all'Autorità di Controllo"""
    return templates.TemplateResponse(request=request, name="dashboard_authority.html")

@ui_router.get("/lista-utenti", response_class=HTMLResponse)
async def lista_utenti(request: Request, current_user: User = Depends(has_role_in([ruolo.AUTORITY]))):
    """Lista degli utenti registrati"""
    return templates.TemplateResponse(request=request, name="lista_utenti.html")

@ui_router.get("/admin/prenota", response_class=HTMLResponse)
async def admin_prenota(request: Request, current_user: User = Depends(has_role_in([ruolo.AUTORITY]))):
    """Prenotazione lato admin"""
    return templates.TemplateResponse(request=request, name="prenotazione_admin.html")

@ui_router.get("/dettagliutente/{id}", response_class=HTMLResponse)
async def dettagli_utente(id: UUID, request: Request, current_user: User = Depends(has_role_in([ruolo.AUTORITY]))):
    """Dettagli visite utente"""
    return templates.TemplateResponse(request=request, name="admin_visite_utente.html", context={
        "id": id
    })

@ui_router.get("/errore", response_class=HTMLResponse)
async def errore(request: Request):
    """Qualcosa è andato storto"""
    return templates.TemplateResponse(request=request, name="pagina_errore.html")
