from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.models.schemas import UserCreate, UserResponse, LoginRequest, Token, VisitCreate, VisitUpdate, VisitResponse, EvidenceCreate
from app.service.user_service import UserService
from app.service.visit_service import VisitService

from app.core.security import get_current_user, has_role_in
from app.core.re_monitor import public_monitor
from app.db.models import User, Visit#, Disponibilita
from app.enum.ruolo import ruolo
from app.enum.prova import TipoProva, PROVE_RUOLI

router = APIRouter(dependencies=[Depends(public_monitor)])

# READ users
@router.get("/getusers")
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) # aggiunto controllo
):
    return await UserService.get_active_users_with_role(ruolo.MEDICO, db)

@router.get("/getusers/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
