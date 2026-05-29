from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship
)
from sqlalchemy import Column, String, UUID, Boolean, Enum, DateTime, ForeignKey, ForeignKeyConstraint, CheckConstraint, UniqueConstraint
from app.enum.ruolo import ruolo as rules
from app.enum.prova import TipoProva
import uuid
from datetime import datetime
from typing import Optional, List

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        index=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    attivo: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    ruolo: Mapped[rules] = mapped_column(
        Enum(
            rules,
            values_callable=lambda obj: [e.value for e in obj]
        ),
        nullable=False
    )

    __table_args__ = (
        # coppie (id, ruolo) uniche in tabella (necessario per foreign key)
        UniqueConstraint("id", "ruolo", name="uq_users_id_ruolo"), 
    )

class Visit(Base):
    __tablename__ = "visits"
    confermata: Mapped[bool] = mapped_column(Boolean, default=False)
    id = Column(UUID(), primary_key=True, index=True)
    paziente = Column(UUID(), nullable=False)
    medico = Column(UUID(), nullable=True, default=None)
    timestamp = Column(DateTime(timezone=True), nullable=True, default=None)

    # per vincolare il ruolo degli utenti coinvolti nella visita
    ruolo_paziente = Column(
        Enum(rules, values_callable=lambda obj: [e.value for e in obj]), 
        CheckConstraint("ruolo_paziente = 'utente'"), 
        nullable=False, default=rules.PAZIENTE
    )
    ruolo_medico = Column(
        Enum(rules, values_callable=lambda obj: [e.value for e in obj]), 
        CheckConstraint("ruolo_medico = 'staff'"), 
        nullable=False, default=rules.MEDICO
    )

    prove: Mapped[List["Evidence"]] = relationship(
        cascade="all, delete-orphan", 
        lazy="selectin"
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
        ), 
        UniqueConstraint("medico", "timestamp", name="unique_medico_timestamp") 
    )

class Evidence(Base):
    __tablename__ = "evidences"

    visita: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey(
            "visits.id",
            ondelete="CASCADE"
        ),
        primary_key=True,
        nullable=False
    )
    tipo: Mapped[TipoProva] = mapped_column(
        Enum(
            TipoProva,
            values_callable=lambda obj: [e.value for e in obj]
        ),
        primary_key=True,
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("visita", "tipo", name="unique_visita_tipo"), 
    )

class Disponibilita(Base):
    __tablename__ = "disponibilita"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    medico = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    occupato = Column(Boolean, default=False)

