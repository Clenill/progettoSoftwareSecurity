
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
import sqlalchemy.exc as exc
from sqlalchemy.orm import joinedload
from app.enum.prova import TipoProva
from app.db.models import Visit, Evidence, User
from app.models.schemas import VisitCreate, VisitUpdate
from datetime import timezone
from app.core.exceptions import InvalidVisitDateException
from datetime import datetime, timezone

class VisitRepository:

    @staticmethod
    async def create(
        db: AsyncSession, 
        visit_data: VisitCreate, 
        user: User, 
        commit: bool = True):
        if visit_data.timestamp is not None and visit_data.timestamp <= datetime.now(timezone.utc):
            raise InvalidVisitDateException()
        confermata = visit_data.confermata
        if confermata == None:
            confermata = False
        visit = Visit(
            id = uuid4(), 
            paziente = visit_data.paziente, 
            medico = visit_data.medico, 
            timestamp = visit_data.timestamp, 
            confermata = confermata
        )

        db.add(visit)
        await db.flush()
        if commit:
            await db.commit()
            await db.refresh(visit)
        return visit
    
    @staticmethod
    async def get_all(db: AsyncSession, user: User | None = None):
        statement = select(Visit).options(joinedload(Visit.prove))
        if user:
            statement = statement.where(
                or_(Visit.paziente == user.id, Visit.medico == user.id)
            )
        return (await db.execute(statement)).scalars().unique().all()
    
    @staticmethod
    async def get_by_id(db: AsyncSession, id: UUID, user: User | None = None):
        statement = (
            select(Visit)
            .options(joinedload(Visit.prove))
            .where(Visit.id == id)
        )
        if user:
            statement = statement.where(
                or_(Visit.paziente == user.id, Visit.medico == user.id)
            )
        return (await db.execute(statement)).unique().scalar_one_or_none()
    
    @staticmethod
    async def edit_visit(
        db: AsyncSession, 
        id: UUID, 
        user: User | None, 
        visit_data: VisitUpdate, 
        commit: bool = True
    ):
        visit = await VisitRepository.get_by_id(db, id, user)
        if not visit:
            raise exc.NoResultFound("Visita non trovata")
        data = visit_data.model_dump(exclude_unset=True)
        for k,v in data.items():
            setattr(visit, k, v)
        if commit:
            await db.commit()
            await db.refresh(visit)
        return visit
    
    @staticmethod
    async def delete_visit(db: AsyncSession, id: UUID, commit: bool = True):
        visit = await VisitRepository.get_by_id(db, id)
        if not visit:
            raise exc.NoResultFound("Visita non trovata")
        else:
            await db.delete(visit)
            if commit:
                await db.commit()

    @staticmethod
    async def add_evidence(
        db: AsyncSession, 
        id: UUID, 
        tipo: TipoProva, 
        user: User | None, 
        commit: bool = True
    ):
        visit = await VisitRepository.get_by_id(db, id, user)
        if not visit:
            raise exc.NoResultFound("Visita non trovata")
        evidences = set((await db.execute(
            select(Evidence.tipo).where(Evidence.visita == id)
        )).scalars().all())

        if tipo in evidences:
            raise ValueError("Prova già inserita")
        
        evidence = Evidence(
            visita = id, 
            tipo = tipo
        )

        db.add(evidence)
        if commit:
            await db.commit()
            await db.refresh(evidence)
        return evidence
    
    @staticmethod
    async def get_visits_by_doctor(db: AsyncSession, medico_id: UUID):
        # Recupera tutte le visite per un dato medico
        result = await db.execute(
            select(Visit).where(Visit.medico == medico_id)
        )
        return result.scalars().all()

    @staticmethod
    async def confirm_visit(db: AsyncSession, visit_id: UUID, commit: bool = True):
        visit = await db.get(Visit, visit_id)
        if not visit:
            raise Exception("Visita non trovata")
        visit.confermata = True
        if commit:
            await db.commit()
            await db.refresh(visit)
        return visit

