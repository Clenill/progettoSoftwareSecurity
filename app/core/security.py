from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

from fastapi import Depends, HTTPException, Cookie, Request
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import InvalidCredentials

from app.db.database import get_db
from app.db.models import User
from app.enum.ruolo import ruolo
import bcrypt

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

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

# Calcola il momento in cui il token smette di funzionare. Ora è 30 minuti
# COntrollo automatico. Se il tempo è scaduto restituisce 401
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user_parent(fail_without_exception: bool = False):
    async def _get_current_user(
        access_token: str | None = Cookie(None), 
        db: AsyncSession = Depends(get_db)
    ):
        if not access_token:
            if fail_without_exception:
                return None
            raise InvalidCredentials()

        try:
            if access_token.startswith("Bearer "):
                access_token = access_token.replace("Bearer ", "")

            payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("sub")

            if email is None or not isinstance(email, str):
                if fail_without_exception:
                    return None
                raise InvalidCredentials()
        except:
            if fail_without_exception:
                return None
            raise InvalidCredentials()

        from app.service.user_service import UserService
        user = await UserService.get_user_by_email(email, db)

        if not fail_without_exception and user is None:
            raise InvalidCredentials()

        return user

    return _get_current_user

get_current_user = get_current_user_parent(False)
get_current_user_or_none = get_current_user_parent(True)

def has_role_in(roles: list[ruolo]):
    def _has_role_in(user: User = Depends(get_current_user)):
        if user.ruolo not in roles:
            raise HTTPException(status_code=403)
        return user
    return _has_role_in

def sanitize_str(text: str):
    if not text: return ""
    return (text.replace("\n", "\\n")
        .replace("\r", "\\r")
        .strip()
    )

def get_client_metadata(request: Request):
    ip = None
    for k,v in request.headers.items():
        if k == "x-forwarded-for":
            ip = sanitize_str(v.split(",")[0])
            break
    if ip is None:
        ip = sanitize_str(request.client.host if request.client else "127.0.0.1")
    email, role = None, ruolo.PAZIENTE
    auth_header = request.cookies.get("access_token")
    if auth_header:
        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = sanitize_str(str(payload.get("sub", None)))
            role = payload.get("role", "user")
        except:
            email = "invalid token"
    return ip, email, role

