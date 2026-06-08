from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.schemas import (
    UserCreate,
    UserResponse,
    LoginRequest,
    Token
)
from app.service.user_service import UserService
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/register", response_model=UserResponse)
async def register(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    return await UserService.create_user(user, db)


@router.post("/login")
async def login(
    login_data: LoginRequest,
    response: Response, 
    db: AsyncSession = Depends(get_db)
):
    token, user = await UserService.authenticate_user(login_data, db)
    response.set_cookie(
        key="access_token", 
        value=token["access_token"], 
        httponly=True, 
        secure=False, # solo HTTPS se true
        samesite="lax", 
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60, 
        path="/"
    )

    return {
        "message": "Login effettuato con successo", 
        "role": user.ruolo
    }

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="access_token", 
        path="/", 
        httponly=True, 
        secure=False, 
        samesite="lax"
    )
    return { "message": "Logout effettuato con successo" }

