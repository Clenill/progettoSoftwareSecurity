from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import User, Visit, Disponibilita
from app.core.security import get_current_user, has_role_in
from app.core.exceptions import UserNotAuthorizedException
from app.models.schemas import VisitCreate, VisitUpdate, VisitResponse, EvidenceCreate
from app.enum.ruolo import ruolo
from app.service.visit_service import VisitService

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

# Controllo di autorizzazione basato sui ruoli
@router.get("/admin-only")
async def accesso_admin(current_user: User = Depends(get_current_user)):
    if current_user.ruolo != "admin":
        raise UserNotAuthorizedException()
    return {"message": "Benvenuto!"}

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