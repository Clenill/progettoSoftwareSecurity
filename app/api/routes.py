from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.db.database import get_db
from app.db.models import User
from app.models.schemas import UserCreate, UserResponse
from app.core.security import hash_password
from app.enum.ruolo import ruolo

router = APIRouter()

@router.get("/")
def test():
    return {"message": "API OK"}

# READ users
@router.get("/getusers")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users

@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    
    # 🔍 controllo email già esistente
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email già registrata")
    
    print("PASSWORD BYTES:", len(user.password.encode("utf-8")))
# 🔐 hashing password
    hashed_pw = hash_password(user.password)

    # ✅ creazione utente
    new_user = User(
        id= uuid.uuid4(),
        name=user.name,
        email=user.email,
        hashed_password=hashed_pw,
        attivo=user.attivo,
        ruolo= user.ruolo
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user