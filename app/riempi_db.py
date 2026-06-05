import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from app.db.database import SessionLocal
from app.db.models import User, Visit
from app.core.security import hash_password
from app.enum.ruolo import ruolo
from app.db.models import Disponibilita

from app.service.contract_service import ContractService


async def aggiungi_disponibilita_fittizia(db, medico_id):
    # Generazione disponibilità per i prossimi 7 giorni
    start_date = datetime.now()
    
    for i in range(7):
        giorno = start_date + timedelta(days=i)
        orari = ["09:00", "11:00", "15:00"]
        
        for orario in orari:
            # Formattazione timestamp completo
            timestamp_str = f"{giorno.strftime('%Y-%m-%d')} {orario}:00"
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            
            # Creazione oggetto disponibilità (adatta al tuo modello)
            nuova_disponibilita = Disponibilita(
                medico=medico_id,
                timestamp=timestamp,
                occupato=False
            )
            db.add(nuova_disponibilita)
    
    await db.commit()
    print("Disponibilità fittizie aggiunte con successo!")


async def seed():
    from sqlalchemy import delete
    async with SessionLocal() as db:
        await db.execute(delete(Visit))
        await db.execute(delete(User))
        
        await db.commit()
    async with SessionLocal() as db:
        # Creazione autorità
        autorita_id = uuid.uuid4()
        autorita = User(
            id=autorita_id,
            name="Direzione Ospedale",
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
        
        db.add_all([autorita, medico, paziente])
        await db.commit()

        # Creazione visita fittizia
        visita = Visit(
            id=uuid.uuid4(),
            paziente=paziente_id,
            medico=medico_id,
            timestamp=datetime.now(timezone.utc), # Data corrente
            ruolo_paziente=ruolo.PAZIENTE,
            ruolo_medico=ruolo.MEDICO,
            confermata=True
        )
        
        db.add(visita)
        await db.commit()
        print("Dati di prova inseriti con successo!")
        # La visita è confermata => va inserita nel contratto
        await db.refresh(visita)
        await ContractService.add_visit(medico, visita)
        await aggiungi_disponibilita_fittizia(db, medico_id)

if __name__ == "__main__":
    asyncio.run(seed())
