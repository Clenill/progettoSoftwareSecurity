from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, UUID, Boolean, Enum, DateTime, ForeignKey, ForeignKeyConstraint, CheckConstraint, UniqueConstraint
from app.enum.ruolo import ruolo
from pydantic import UUID4
from datetime import datetime
from typing import Optional

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    attivo = Column(Boolean, default=False)
    ruolo = Column(
        Enum(
            ruolo,
            values_callable=lambda obj: [e.value for e in obj]
        ),
        nullable=False
    )

    __table_args__ = (
        # coppie (id, ruolo) uniche in tabella (necessario per foreign key)
        UniqueConstraint("id", "ruolo", name="unique_users_id_ruolo"), 
    )

class Visit(Base):
    __tablename__ = "visits"

    id = Column(UUID(), primary_key=True, index=True)
    paziente = Column(UUID(), nullable=False)
    medico = Column(UUID(), nullable=True, default=None)
    timestamp = Column(DateTime(timezone=True), nullable=True, default=None)

    # per vincolare il ruolo degli utenti coinvolti nella visita
    ruolo_paziente = Column(
        Enum(ruolo, values_callable=lambda obj: [e.value for e in obj]), 
        CheckConstraint("ruolo_paziente = 'utente'"), 
        nullable=False, default=ruolo.PAZIENTE
    )
    ruolo_medico = Column(
        Enum(ruolo, values_callable=lambda obj: [e.value for e in obj]), 
        CheckConstraint("ruolo_medico = 'staff'"), 
        nullable=False, default=ruolo.MEDICO
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["paziente", "ruolo_paziente"], 
            ["users.id", "users.ruolo"], 
            ondelete="CASCADE", 
            onupdate="CASCADE"
        ), 
        ForeignKeyConstraint(
            ["medico", "ruolo_medico"], 
            ["users.id", "users.ruolo"], 
            ondelete="CASCADE", 
            onupdate="CASCADE"
        )
    )

