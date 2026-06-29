from fastapi import APIRouter, Depends, Response, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.models import Visit

from app.db.database import get_db
from app.models.schemas import VisitCreate, VisitUpdate, VisitResponse, EvidenceCreate
from app.service.visit_service import VisitService
from app.core.exceptions import *
from app.core.security import get_current_user, has_role_in
from app.core.re_monitor import public_monitor
from app.db.models import User
from app.enum.ruolo import ruolo
from app.enum.prova import PROVE_RUOLI
from uuid import UUID
from datetime import datetime, timezone, date
from app.repositories.visit_repository import VisitRepository

router = APIRouter(
    prefix="/visit",
    tags=["Visit"], 
    dependencies=[Depends(public_monitor)]
)

@router.post("/newvisit", response_model=VisitResponse)
async def create_visit(
    visit: VisitCreate, 
    current_user: User = Depends(has_role_in([ruolo.MEDICO])), 
    db: AsyncSession = Depends(get_db)
):
    # Il medico può creare solo visite proprie
    if current_user.id != visit.medico:
        raise InvalidDoctorIdException()
    
    # Data visita solo nel futuro
    if (
        visit.timestamp is not None 
        and visit.timestamp <= datetime.now(timezone.utc)
    ):
        raise InvalidVisitDateException()
    
    return await VisitService.create_visit(visit, current_user, db)

@router.get("/allmyvisits", response_model=list[VisitResponse])
async def get_all_visits(
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    return await VisitService.get_visits(current_user, db)

@router.get("/dettagliovisita/{id}", response_model=VisitResponse)
async def get_visit_by_id(
    id: UUID, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    return await VisitService.get_visit_by_id(id, current_user, db)

@router.put("/updatevisits/{id}", response_model=VisitResponse)
async def edit_visit(
    visit: VisitUpdate, 
    id: UUID, 
    current_user: User = Depends(has_role_in([ruolo.MEDICO, ruolo.AUTORITY])), 
    db: AsyncSession = Depends(get_db)
):
    if current_user.ruolo == ruolo.AUTORITY:
        return await VisitService.edit_visit(id, visit, None, db)
    if visit.medico and visit.medico != current_user.id:
        raise MissingVisitDetailsException(detail="Il medico può essere cambiato solo dall'autorità")
    
    if visit.timestamp is None:
        raise InvalidVisitDateException()
    
    if visit.timestamp < datetime.now(timezone.utc):
        raise InvalidVisitDateException()
    
    return await VisitService.edit_visit(id, visit, current_user, db)

@router.post("/addevidence/{id}")
async def add_evidence(
    evidence: EvidenceCreate, 
    id: UUID, 
    current_user: User = Depends(has_role_in([ruolo.PAZIENTE, ruolo.MEDICO, ruolo.AUTORITY])), 
    db: AsyncSession = Depends(get_db)
):
    if evidence.tipo not in PROVE_RUOLI[current_user.ruolo]:
        raise InvalidCredentials()
    
    await VisitService.add_evidence(id, evidence.tipo, current_user, db)
    return { 
        "message": "Prova aggiunta con successo",
        "visit_id": id,
        "evidence_type": evidence.tipo
        }

@router.get("/disponibilita/{medico_id}")
async def visite_disponibili_medico(
    medico_id: UUID,
    giorno: date = Query(..., alias="giorno"),
    db: AsyncSession = Depends(get_db)
):
    return await VisitService.get_available_slots(
        medico_id,
        giorno,
        db
    )

@router.get("/visits/my-agenda")
async def get_my_agenda(
    current_user: User = Depends(has_role_in([ruolo.MEDICO])),
    db: AsyncSession = Depends(get_db)
):
    # Ritorna tutte le visite assegnate a questo medico
    return await VisitRepository.get_visits_by_doctor(db, current_user.id)

@router.put("/visits/{id}/confirm")
async def confirm_visit(
    id: UUID,
    current_user: User = Depends(has_role_in([ruolo.MEDICO])),
    db: AsyncSession = Depends(get_db)
):
    #return await VisitRepository.confirm_visit(db, id)
    return await VisitService.confirm_visit(id, db)

@router.post("/visits/prenota", response_model=VisitResponse)
async def prenota_visita(
    visit: VisitCreate, 
    current_user: User = Depends(has_role_in([ruolo.PAZIENTE])), 
    db: AsyncSession = Depends(get_db)
):
    # Il paziente prenota per sé
    if visit.paziente != current_user.id:
        raise UserNotAuthorizedException()
    
    # Il medico deve essere presente per rispettare il modello
    if not visit.medico:
        raise MissingVisitDetailsException(detail="Il medico deve essere specificato")
        
    return await VisitService.create_visit(visit, current_user, db)

@router.get("/visits/all-visits", response_model=list[VisitResponse])
async def get_all_system_visits(
    current_user: User = Depends(has_role_in([ruolo.AUTORITY])), 
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(Visit)
        .options(selectinload(Visit.prove))
        .order_by(Visit.timestamp.desc())
    )
    
    result = await db.execute(query)
    visite = result.scalars().all()
    
    return visite

@router.delete("/denied-visit/{id}")
async def delete_visit(id: UUID, current_user: User = Depends(
    has_role_in([ruolo.MEDICO])
), db: AsyncSession = Depends(get_db)
):
    await VisitService.delete_visit(
        id,
        current_user,
        db
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
