import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.db.models import User
from app.models.schemas import UserCreate, LoginRequest
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password
from app.core.exceptions import *
from app.core.security import hash_password, verify_password, create_access_token
from app.core.security import verify_password, create_access_token
from typing import cast

class UserService:

    @staticmethod
    async def create_user(user_data: UserCreate, db: AsyncSession):

        # controllo email
        existing_user = await UserRepository.get_by_email(
            db,
            user_data.email
        )

        if len(user_data.password.encode("utf-8")) > 72:
            raise PasswordTooLongException()

        if existing_user:
            raise EmailAlreadyExistsException()
        
        # hashing password
        hashed_pw = hash_password(user_data.password)

        # entity/Model
        new_user = User(
            id = uuid.uuid4(),
            name=user_data.name,
            email=user_data.email,
            hashed_password=hashed_pw,
            attivo=user_data.attivo,
            ruolo=user_data.ruolo
        )
        try:
            return await UserRepository.create(db, new_user)
        except IntegrityError:
            await db.rollback()

            raise EmailAlreadyExistsException()
    
    @staticmethod
    async def get_user_by_email(email: str, db:AsyncSession):
        user = await UserRepository.get_by_email(db, email)

        if not user:
            raise UserNotFoundException()
        
        return user
    
    @staticmethod
    async def get_user(db: AsyncSession):
        return await UserRepository.get_all(db)
    
    @staticmethod
    async def authenticate_user(login_data: LoginRequest, db: AsyncSession):
        user = await UserRepository.get_by_email(db, login_data.email)
        
        if not user or not verify_password(login_data.password, cast(str, user.hashed_password)):
            raise InvalidCredentials()
        
        if not cast(bool, user.attivo):
            raise UserNotActive()

        # Generiamo il token includendo email e ruolo (opzionale)
        token_data = {"sub": user.email, "role": user.ruolo}
        token = create_access_token(token_data)
        
        return {"access_token": token, "token_type": "bearer"}