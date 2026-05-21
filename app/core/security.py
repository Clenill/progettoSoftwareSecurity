from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import User
from app.enum.ruolo import ruolo

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dove FastAPI deve cercare il token
oauth2_scheme = APIKeyHeader(name="Authorization", auto_error=False)

load_dotenv()

_secret_key = os.getenv("SECRET_KEY")
_algorithm = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

if _secret_key is None:
    raise ValueError("SECRET_KEY non configurata")
if _algorithm is None:
    raise ValueError("ALGORITHM non configurato")

SECRET_KEY: str = _secret_key
ALGORITHM: str = _algorithm

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
        email = payload.get("sub")

        if email is None or not isinstance(email, str):
            raise credentials_exception
    except:
        raise credentials_exception
    
    # Ricerca utente nel DB - Usa il metodo statico della classe
    from app.service.user_service import UserService
    user = await UserService.get_user_by_email(email, db)
    
    if user is None:
        raise credentials_exception
        
    return user

def has_role_in(roles: list[ruolo]):
    def _has_role_in(user: User = Depends(get_current_user)):
        if user.ruolo not in roles:
            raise HTTPException(status_code=403)
        return user
    return _has_role_in

