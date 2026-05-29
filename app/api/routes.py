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

router = APIRouter()

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



@router.get("/disponibilita/{medico_id}")
async def get_disponibilita(medico_id: str, db: AsyncSession = Depends(get_db)):
    query_slots = select(Disponibilita).where(Disponibilita.medico == medico_id , Disponibilita.occupato == False).order_by(Disponibilita.timestamp)
    result_slots = await db.execute(query_slots)
    tutti_gli_slot = result_slots.scalars().all()
    
    return [{
    "data": s.timestamp.strftime("%d/%m/%Y"), 
    "orario": s.timestamp.strftime("%H:%M"),
    # isofromat() manterrà l'informazione UTC corretta
    "valore": s.timestamp.isoformat() 
} for s in tutti_gli_slot]

@router.get("/getusers/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user