
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound
from app.repositories.visit_repository import VisitRepository
from app.models.schemas import VisitCreate, VisitUpdate, EvidenceCreate
from app.db.models import User, Evidence
from app.enum.ruolo import ruolo
from app.enum.prova import TipoProva
from uuid import UUID

class VisitService:

    @staticmethod
    async def create_visit(
        visit_data: VisitCreate, 
        user: User, 
        db: AsyncSession
    ):
        try:
            return await VisitRepository.create(db, visit_data, user)
        except IntegrityError:
            raise HTTPException(status_code=400, detail="Dati visita errati")

    @staticmethod
    async def get_visits(user: User | None, db: AsyncSession):
        return await VisitRepository.get_all(db, user)

    @staticmethod
    async def get_visit_by_id(id: UUID, user: User | None, db: AsyncSession):
        visit = await VisitRepository.get_by_id(db, id, user)
        if not visit:
            raise HTTPException(status_code=404, detail="Visita non trovata")
        return visit

    @staticmethod
    async def edit_visit(
        id: UUID, 
        visit_data: VisitUpdate, 
        user: User | None, 
        db: AsyncSession
    ):
        try:
            visit = (await VisitRepository.edit_visit(db, id, user, visit_data))
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
    async def delete_visit(id: UUID, db: AsyncSession):
        try:
            await VisitRepository.delete_visit(db, id)
        except NoResultFound as err:
            raise HTTPException(
                status_code=404, 
                detail=str(err)
            )
    
    @staticmethod
    async def add_evidence(
        id: UUID, 
        tipo: TipoProva, 
        user: User, 
        db: AsyncSession
    ):
        try:
            await VisitRepository.add_evidence(db, id, tipo, user)
        except NoResultFound as e:
            raise HTTPException(
                status_code=404, 
                detail=str(e)
            )
        except ValueError as e:
            raise HTTPException(
                status_code=409, # CONFLICT
                detail=str(e)
            )

