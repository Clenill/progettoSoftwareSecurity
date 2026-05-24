from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.models.schemas import UserCreate, UserResponse, LoginRequest, Token, VisitCreate, VisitUpdate, VisitResponse, EvidenceCreate
from app.service.user_service import UserService
from app.service.visit_service import VisitService

from app.core.security import get_current_user, has_role_in
from app.db.models import User, Visit, Disponibilita
from app.enum.ruolo import ruolo
from app.enum.prova import TipoProva, PROVE_RUOLI
from uuid import UUID
from datetime import datetime, timezone

router = APIRouter()

@router.get("/")
def test():
    return {"message": "API OK"}

# READ users
@router.get("/getusers")
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) # aggiunto controllo
):
    return await UserService.get_user(db)

@router.get("/users/byemail", response_model=UserResponse)
async def get_user_by_email(
    email: str,
    db: AsyncSession = Depends(get_db)
):
    return await UserService.get_user_by_email(email, db)

# Controllo di autorizzazione basato sui ruoli
@router.get("/admin-only")
async def accesso_admin(current_user: User = Depends(get_current_user)):
    if current_user.ruolo != "admin":
        raise HTTPException(status_code=403, detail="Accesso consentito solo agli admin")
    return {"message": "Benvenuto!"}

@router.post("/visits", response_model=VisitResponse)
async def create_visit(
    visit: VisitCreate, 
    current_user: User = Depends(has_role_in([ruolo.MEDICO, ruolo.AUTORITY])), 
    db: AsyncSession = Depends(get_db)
):
    is_owner = current_user.id in { visit.medico, visit.paziente }
    if current_user.ruolo != ruolo.AUTORITY and not is_owner:
        raise HTTPException(status_code=403)
    if current_user.ruolo == ruolo.MEDICO:
        if current_user.id != visit.medico:
            raise HTTPException(
                status_code=403, 
                detail="Il medico indicato non corrisponde all'utente corrente"
            )
        if visit.timestamp and visit.timestamp <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=400, 
                detail="La visita non può essere nel passato"
            )
    return await VisitService.create_visit(visit, current_user, db)

@router.get("/visits", response_model=list[VisitResponse])
async def get_visits(
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    if current_user.ruolo == ruolo.AUTORITY:
        return await VisitService.get_visits(None, db)
    return await VisitService.get_visits(current_user, db)

@router.post("/visits/prenota", response_model=VisitResponse)
async def prenota_visita(
    visit: VisitCreate, 
    current_user: User = Depends(has_role_in([ruolo.PAZIENTE])), 
    db: AsyncSession = Depends(get_db)
):
    # Il paziente prenota per sé
    if visit.paziente != current_user.id:
        raise HTTPException(status_code=403, detail="Non autorizzato")
    
    # Il medico deve essere presente per rispettare il modello
    if not visit.medico:
        raise HTTPException(status_code=400, detail="Il medico deve essere specificato")
        
    return await VisitService.create_visit(visit, current_user, db)

@router.get("/visits/{id}", response_model=VisitResponse)
async def get_visit_by_id(
    id: UUID, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    if current_user.ruolo == ruolo.AUTORITY:
        return await VisitService.get_visit_by_id(id, db)
    return await VisitService.get_visit_by_id(id, current_user, db)

@router.put("/visits/{id}", response_model=VisitResponse)
async def edit_visit(
    visit: VisitUpdate, 
    id: UUID, 
    current_user: User = Depends(has_role_in([ruolo.MEDICO, ruolo.AUTORITY])), 
    db: AsyncSession = Depends(get_db)
):
    if current_user.ruolo == ruolo.AUTORITY:
        return await VisitService.edit_visit(id, visit, None, db)
    if visit.medico and visit.medico != current_user.id:
        raise HTTPException(
            status_code=400, 
            detail="Il medico può essere cambiato solo dall'autorità"
        )
    if visit.timestamp < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=400, 
            detail="La visita non può essere nel passato"
        )
    return await VisitService.edit_visit(id, visit, current_user, db)

@router.delete("/visits/{id}")
async def delete_visit(
    id: UUID, 
    current_user: User = Depends(has_role_in([ruolo.AUTORITY])), 
    db: AsyncSession = Depends(get_db)
):
    await VisitService.delete_visit(id, db)
    return { "message": "Visita eliminata" }

@router.post("/visits/{id}")
async def add_evidence(
    evidence: EvidenceCreate, 
    id: UUID, 
    current_user: User = Depends(has_role_in([ruolo.PAZIENTE, ruolo.MEDICO])), 
    db: AsyncSession = Depends(get_db)
):
    if evidence.tipo not in PROVE_RUOLI[current_user.ruolo]:
        raise HTTPException(
            status_code=403, 
            detail="Prova non ammessa per il ruolo corrente"
        )
    await VisitService.add_evidence(id, evidence.tipo, current_user, db)
    return { "message": "Prova aggiunta" }

@router.get("/disponibilita/{medico_id}")
async def get_disponibilita(medico_id: str, db: AsyncSession = Depends(get_db)):
    query_slots = select(Disponibilita).where(Disponibilita.medico == medico_id).order_by(Disponibilita.timestamp)
    result_slots = await db.execute(query_slots)
    tutti_gli_slot = result_slots.scalars().all()
  
    query_visite = select(Visit.timestamp).where(Visit.medico == medico_id)
    result_visite = await db.execute(query_visite)
    
    visite_prenotate = []
    for v in result_visite.all():
        dt = v[0]
        if dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)
        visite_prenotate.append(dt)
    slots_disponibili = []
    for s in tutti_gli_slot:
        s_ts = s.timestamp
        if s_ts.tzinfo is not None:
            s_ts = s_ts.replace(tzinfo=None)
        
        if s_ts not in visite_prenotate:
            slots_disponibili.append(s)
    return [{
    "data": s.timestamp.strftime("%d/%m/%Y"), 
    "orario": s.timestamp.strftime("%H:%M"),
    # isofromat() manterrà l'informazione UTC corretta
    "valore": s.timestamp.isoformat() 
} for s in slots_disponibili]

@router.get("/getusers/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user