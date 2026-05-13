from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.schemas import UserCreate, UserResponse
from app.service.user_service import UserService
from app.models.schemas import UserCreate, UserResponse, LoginRequest, Token

from app.core.security import get_current_user
from app.db.models import User

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

@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await UserService.create_user(user, db)

@router.get("/users/byemail", response_model=UserResponse)
async def get_user_by_email(
    email: str,
    db: AsyncSession = Depends(get_db)
):
    return await UserService.get_user_by_email(email, db)


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await UserService.authenticate_user(login_data, db)

# Controllo di autorizzazione basato sui ruoli
@router.get("/admin-only")
async def accesso_admin(current_user: User = Depends(get_current_user)):
    if current_user.ruolo != "admin":
        raise HTTPException(status_code=403, detail="Accesso consentito solo agli admin")
    return {"message": "Benvenuto!"}