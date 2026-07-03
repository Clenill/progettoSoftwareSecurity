
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound
from app.repositories.visit_repository import VisitRepository
from app.models.schemas import VisitCreate, VisitUpdate, EvidenceCreate
from app.db.models import User, Evidence
from app.enum.ruolo import ruolo
from app.enum.prova import TipoProva
from uuid import UUID
from datetime import datetime, timezone, timedelta, date, time
from app.core.exceptions import *
from app.service.user_service import UserService
from zoneinfo import ZoneInfo
import os

class VisitService:

    @staticmethod
    async def create_visit(
        visit_data: VisitCreate, 
        user: User, 
        db: AsyncSession
    ):
        if visit_data.timestamp is None:
            raise MissingVisitDetailsException(detail="Timestamp visita obbligatorio.")
        
        durata_minuti = int(os.getenv('DURATA_VISITA', '10'))
        
        duration = timedelta(minutes=int(durata_minuti))
        visit_time = visit_data.timestamp
        tz = ZoneInfo("Europe/Rome")
        # Timezone-aware
        if visit_time.tzinfo is None:
            visit_time = visit_time.replace(tzinfo=tz) # o ZoneInfo("Europe/Rome"
        start_window = visit_time
        end_window = visit_time + duration

        existing_visit = (
            await VisitRepository.get_doctor_visits_between(
                db=db, doctor_id=visit_data.medico, 
                start_time=start_window, end_time=end_window
            )
        )

        if existing_visit:
            raise VisitTimeConflictException()

        try:
            return await VisitRepository.create(db, visit_data, user)
        except IntegrityError:
            raise MissingVisitDetailsException(detail="Dati visita errati.")

    @staticmethod
    async def get_available_slots(doctor_id: UUID, day: date, db: AsyncSession):

        tz = ZoneInfo("Europe/Rome")
        start_day = datetime.combine(day, time(8,0), tz)
        end_day = datetime.combine(day, time(18,0), tz)
        visits = await VisitRepository.get_doctor_visits_by_day(
            db, doctor_id, start_day, end_day
            )
        occupied = {
            visit.timestamp.astimezone(timezone.utc)
            for visit in visits
            if visit.timestamp is not None
        }
        duration = timedelta(
            minutes=int(os.getenv("DURATA_VISITA",60))
        )
        slots = []
        current = start_day
        print("OCCUPIED:", occupied)
        print("PRIMO SLOT:", start_day.astimezone(timezone.utc))
        while current < end_day:

            if current not in occupied and current > datetime.now(tz):

                slots.append({
                    "timestamp": current.isoformat(),
                    "orario": current.strftime("%H:%M")
                })
            current += duration

        return slots

    @staticmethod
    async def get_visits(user: User | None, db: AsyncSession):
        return await VisitRepository.get_all(db, user)

    @staticmethod
    async def get_visit_by_id(id: UUID, user: User | None, db: AsyncSession):
        visit = await VisitRepository.get_by_id(db, id, user)
        if not visit:
            raise MissingVisitDetailsException(detail="Visita non trovata.")
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
            raise MissingVisitDetailsException(detail="Visita non trovata.")
        except IntegrityError as err:
            raise MissingVisitDetailsException(detail="Dati visita errati.")
        return visit
    
    @staticmethod
    async def add_evidence(
        id: UUID, 
        tipo: TipoProva, 
        user: User | None, 
        db: AsyncSession
    ):
        try:
            await VisitRepository.add_evidence(db, id, tipo, user)
        except NoResultFound as e:
            raise MissingVisitDetailsException(detail="Visita non trovata.")
        except ValueError as e:
            raise HTTPException(
                status_code=409, # CONFLICT
                detail=str(e)
            )

    @staticmethod
    async def admin_create_visit(
        visit: VisitCreate,
        db: AsyncSession,
        current_user: User
    ):
        if (
            visit.timestamp is not None
            and visit.timestamp <= datetime.now(timezone.utc)
        ):
            raise InvalidVisitDateException()
        
        medico = await UserService.get_user_by_id(
            visit.medico,
            db
        )

        paziente = await UserService.get_user_by_id(
            visit.paziente,
            db
        )

        if medico.ruolo != ruolo.MEDICO:
            raise InvalidUserRoleException(detail="Ruolo Medico non corrisponde all'Id utente.")
        if paziente.ruolo != ruolo.PAZIENTE:
            raise InvalidUserRoleException(detail="Ruolo Paziente non corrisponde all'Id utente.")
        
        return await VisitRepository.create(
            db,
            visit,
            current_user
        )
    
    @staticmethod
    async def agenda_response_medico(db: AsyncSession, current_id: UUID):
        return await VisitRepository.get_agenda_with_names(db, current_id)

    @staticmethod
    async def delete_visit(visit_id: UUID, current_user: User, db: AsyncSession):

        user = None
        if current_user.ruolo != ruolo.AUTORITY:
            user = current_user

        visit = await VisitRepository.get_by_id(db, visit_id, user)

        if not visit:
            raise VisitNotFoundException()
        
        # Solo il medico assegnato può rimuovere la visita
        # L'admin può rimuovere qualsiasi visita non confermata
        if (visit.medico != current_user.id and current_user.ruolo != ruolo.AUTORITY):
            raise UserNotAuthorizedException()
        
        # Non cancellabile se confermata
        if visit.confermata:
            raise VisitAlreadyConfirmedException()
        
        # Visita già avvenuta
        if (
            visit.timestamp is not None and
            visit.timestamp <= datetime.now(timezone.utc)
        ):
            raise VisitAlreadyOccurredException()
        
        await VisitRepository.delete_visit(db, visit)
        
    @staticmethod
    async def confirm_visit(id: UUID, db: AsyncSession):
        return await VisitRepository.confirm_visit(db, id)

