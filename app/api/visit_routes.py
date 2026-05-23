from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.schemas import VisitCreate, VisitUpdate, VisitResponse, EvidenceCreate
from app.service.visit_service import VisitService
from app.core.exceptions import InvalidDoctorIdException, InvalidVisitDateException
from app.core.security import get_current_user, has_role_in
from app.db.models import User
from app.enum.ruolo import ruolo
from app.enum.prova import PROVE_RUOLI
from uuid import UUID
from datetime import datetime, timezone

router = APIRouter(
    prefix="/visit",
    tags=["Visit"]
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

@router.get("/visits", response_model=list[VisitResponse])
async def get_visits(
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    if current_user.ruolo == ruolo.AUTORITY:
        return await VisitService.get_visits(None, db)
    return await VisitService.get_visits(current_user, db)

@router.get("/dettagliovisita/{id}", response_model=VisitResponse)
async def get_visit_by_id(
    id: UUID, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
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
    
    if visit.timestamp is None:
        raise InvalidVisitDateException()
    
    if visit.timestamp < datetime.now(timezone.utc):
        raise InvalidVisitDateException()
    
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
