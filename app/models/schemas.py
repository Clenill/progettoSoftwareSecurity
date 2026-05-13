from pydantic import BaseModel, EmailStr, UUID4, Field
from app.enum.ruolo import ruolo as rules
from datetime import datetime
from typing import Optional
import uuid

# dati in ingresso (request)
class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=25)
    email: EmailStr
    password: str = Field(min_length=3, max_length=72)
    attivo: bool = False
    ruolo: rules

# dati in uscita (response)
class UserResponse(BaseModel):
    id: UUID4
    name: str
    email: EmailStr
    attivo: bool
    ruolo: rules

    class Config:
        from_attributes = True  # necessario per SQLAlchemy

class VisitCreate(BaseModel):
    paziente: UUID4
    medico: Optional[UUID4] = None
    timestamp: Optional[datetime] = None

class VisitUpdate(BaseModel):
    paziente: Optional[UUID4] = None
    medico: Optional[UUID4] = None
    timestamp: Optional[datetime] = None

class VisitResponse(BaseModel):
    id: UUID4
    paziente: UUID4
    medico: Optional[UUID4]
    timestamp: Optional[datetime]

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

