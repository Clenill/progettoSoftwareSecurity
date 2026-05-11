from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, UUID, Boolean, Enum

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    attivo = Column(Boolean)
    ruolo = Column(String)
