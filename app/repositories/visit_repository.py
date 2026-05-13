
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import sqlalchemy.exc as exc
from app.db.models import Visit
from app.models.schemas import VisitCreate, VisitUpdate

class VisitRepository:

    @staticmethod
    async def create(db: AsyncSession, visit_data: VisitCreate):
        visit = Visit(
            id = uuid4(), 
            paziente = visit_data.paziente, 
            medico = visit_data.medico, 
            timestamp = visit_data.timestamp
        )

        db.add(visit)
        await db.commit()
        await db.refresh(visit)
        return visit
    
    @staticmethod
    async def get_all(db: AsyncSession):
        return (await db.execute(select(Visit))).scalars().all()
    
    @staticmethod
    async def get_by_id(db: AsyncSession, id: UUID):
        return (await db.execute(
            select(Visit).where(Visit.id == id)
        )).scalar_one_or_none()
    
    @staticmethod
    async def edit_visit(db: AsyncSession, id: UUID, visit_data: VisitUpdate):
        visit = await VisitRepository.get_by_id(db, id)
        if not visit:
            raise exc.NoResultFound("Visita non trovata")
        data = visit_data.model_dump(exclude_unset=True)
        for k,v in data.items():
            setattr(visit, k, v)
        await db.commit()
        await db.refresh(visit)
        return visit
    
    @staticmethod
    async def delete_visit(db: AsyncSession, id: UUID):
        visit = await VisitRepository.get_by_id(db, id)
        if not visit:
            raise exc.NoResultFound("Visita non trovata")
        else:
            await db.delete(visit)
            await db.commit()
