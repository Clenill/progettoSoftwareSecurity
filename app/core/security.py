from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
import os

from app.db.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dove FastAPI deve cercare il token
oauth2_scheme = APIKeyHeader(name="Authorization", auto_error=False)

# Configurazione DA AGGIUNGERE AL FILE .env
# SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# Calcola il momento in cui il token smette di funzionare. Ora è 30 minuti
# COntrollo automatico. Se il tempo è scaduto restituisce 401
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossibile validare le credenziali",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # AGGIUNGI QUESTE RIGHE: Rimuove "Bearer " se presente
        if token.startswith("Bearer "):
            token = token.replace("Bearer ", "")
            
        # Decodifica JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Ricerca utente nel DB - Usa il metodo statico della classe
    from app.service.user_service import UserService
    user = await UserService.get_user_by_email(email, db)
    
    if user is None:
        raise credentials_exception
        
    return user