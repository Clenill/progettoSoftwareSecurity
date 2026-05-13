
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound
from app.repositories.visit_repository import VisitRepository
from app.models.schemas import VisitCreate, VisitUpdate
from app.db.models import Visit
import uuid

class VisitService:

    @staticmethod
    async def create_visit(visit_data: VisitCreate, db: AsyncSession):
        try:
            return await VisitRepository.create(db, visit_data)
        except IntegrityError:
            raise HTTPException(
                status_code=400, 
                detail="Dati visita errati"
            )

    @staticmethod
    async def get_visits(db: AsyncSession):
        return await VisitRepository.get_all(db)

    @staticmethod
    async def get_visit_by_id(id: uuid.UUID, db: AsyncSession):
        visit = await VisitRepository.get_by_id(db, id)
        if not visit:
            raise HTTPException(
                status_code=404, 
                detail="Visita non trovata"
            )
        return visit

    @staticmethod
    async def edit_visit(id: uuid.UUID, visit_data: VisitUpdate, db: AsyncSession):
        try:
            visit = (await VisitRepository.edit_visit(db, id, visit_data))
        except NoResultFound as err:
            raise HTTPException(
                status_code=404, 
                detail=str("Visita non trovata")
            )
        except IntegrityError as err:
            raise HTTPException(
                status_code=400, 
                detail="Dati visita errati"
            )
        return visit

    @staticmethod
    async def delete_visit(id: uuid.UUID, db: AsyncSession):
        try:
            await VisitRepository.delete_visit(db, id)
        except NoResultFound as err:
            raise HTTPException(
                status_code=404, 
                detail=str(err)
            )
