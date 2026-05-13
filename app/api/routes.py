from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.schemas import UserCreate, UserResponse, VisitCreate, VisitUpdate, VisitResponse
from app.service.user_service import UserService
from app.service.visit_service import VisitService

import uuid

router = APIRouter()

@router.get("/")
def test():
    return {"message": "API OK"}

# READ users
@router.get("/getusers")
async def get_users(db: AsyncSession = Depends(get_db)):
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

@router.get("/visits", response_model=list[VisitResponse])
async def get_visits(db: AsyncSession = Depends(get_db)):
    return await VisitService.get_visits(db)

@router.post("/visits", response_model=VisitResponse)
async def create_visit(visit: VisitCreate, db: AsyncSession = Depends(get_db)):
    return await VisitService.create_visit(visit, db)

@router.put("/visits/{id}", response_model=VisitResponse)
async def edit_visit(visit: VisitUpdate, id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await VisitService.edit_visit(id, visit, db)

@router.delete("/visits/{id}")
async def delete_visit(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await VisitService.delete_visit(id, db)
    return "Visita eliminata"
