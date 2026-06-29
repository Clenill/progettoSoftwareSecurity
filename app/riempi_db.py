import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from app.db.database import SessionLocal
from app.db.models import User, Visit
from app.core.security import hash_password
from app.enum.ruolo import ruolo

async def seed():
    from sqlalchemy import delete
    async with SessionLocal() as db:
        await db.execute(delete(Visit))
        await db.execute(delete(User))
        
        await db.commit()
    async with SessionLocal() as db:
        # Creazione authority
        authority_id = uuid.uuid4()
        authority = User(
            id=authority_id, 
            name="admin", 
            email="admin@ospedale.it", 
            hashed_password=hash_password("password123"), 
            attivo=True, 
            ruolo=ruolo.AUTORITY
        )

        # Creazione medico
        medico_id = uuid.uuid4()
        medico = User(
            id=medico_id,
            name="Dott. Rossi",
            email="rossi@ospedale.it",
            hashed_password=hash_password("password123"),
            attivo=True,
            ruolo=ruolo.MEDICO
        )
        
        # Creazione paziente
        paziente_id = uuid.uuid4()
        paziente = User(
            id=paziente_id,
            name="Mario Bianchi",
            email="mario@email.it",
            hashed_password=hash_password("password123"),
            attivo=True,
            ruolo=ruolo.PAZIENTE
        )
        
        db.add_all([authority, medico, paziente])
        await db.commit()

        # Creazione visita fittizia
        visita = Visit(
            id=uuid.uuid4(),
            paziente=paziente_id,
            medico=medico_id,
            timestamp=datetime.now(timezone.utc), # Data corrente
            ruolo_paziente=ruolo.PAZIENTE,
            ruolo_medico=ruolo.MEDICO,
            confermata = True
        )
        
        db.add(visita)
        await db.commit()
        print("Dati di prova inseriti con successo!")

if __name__ == "__main__":
    asyncio.run(seed())
