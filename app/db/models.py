from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, UUID, Boolean, Enum
from app.enum.ruolo import ruolo

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

