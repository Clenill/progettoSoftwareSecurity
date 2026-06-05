from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import User, Visit, Disponibilita
from app.core.security import get_current_user, has_role_in
from app.core.exceptions import UserNotAuthorizedException, InvalidCredentials
from app.models.schemas import VisitCreate, VisitUpdate, VisitResponse, EvidenceCreate
from app.enum.ruolo import ruolo
from app.enum.prova import PROVE_RUOLI
from app.service.visit_service import VisitService
from app.service.user_service import UserService

from uuid import UUID

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

# La chiamata va triggerata e gli si deve passare id medico e paziente
@router.post("/newvisit", response_model=VisitResponse)
async def admin_create_visit(
    visit: VisitCreate,
    current_user: User = Depends(has_role_in([ruolo.AUTORITY])),
    db: AsyncSession = Depends(get_db)
):
    return await VisitService.admin_create_visit(
        visit,
        db,
        current_user
    )

@router.get("/allvisits", response_model=list[VisitResponse])
async def admin_get_all_visits(
    current_user: User = Depends(has_role_in([ruolo.AUTORITY])), 
    db: AsyncSession = Depends(get_db)
):
    return await VisitService.get_visits(None, db)

@router.put("/updatevisits/{id}", response_model=VisitResponse)
async def edit_visit(
    visit: VisitUpdate, 
    id: UUID, 
    current_user: User = Depends(has_role_in([ruolo.AUTORITY])), 
    db: AsyncSession = Depends(get_db)
):
    return await VisitService.edit_visit(id, visit, None, db)

@router.delete("/deletevisit/{id}")
async def delete_visit(
    id: UUID, 
    current_user: User = Depends(has_role_in([ruolo.AUTORITY])), 
    db: AsyncSession = Depends(get_db)
):
    await VisitService.delete_visit(id, current_user, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    
@router.post("/addevidence/{id}")
async def add_evidence(
    evidence: EvidenceCreate, 
    id: UUID, 
    current_user: User = Depends(has_role_in([ruolo.AUTORITY])), 
    db: AsyncSession = Depends(get_db)
):
    
    await VisitService.add_evidence(id, evidence.tipo, current_user, db)
    return { 
        "message": "Prova aggiunta con successo",
        "visit_id": id,
        "evidence_type": evidence.tipo
        }

@router.post("/activeuser/{id}")
async def active_new_user(
    id:UUID,
    current_user:User = Depends(has_role_in([ruolo.AUTORITY])),
    db: AsyncSession = Depends(get_db)
):
    return UserService.active_user(id, db)
