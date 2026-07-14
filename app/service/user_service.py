import uuid
import re

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.db.models import User
from app.models.schemas import UserCreate, LoginRequest
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password
from app.core.exceptions import *
from app.enum.ruolo import ruolo
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

        UserService.check_name(user_data.name)

        if len(user_data.password) < 8 :
            raise PasswordTooShortException()
        
        UserService.check_password_strength(user_data.password)

        if len(user_data.password.encode("utf-8")) > 72:
            raise PasswordTooLongException()

        if existing_user:
            raise EmailAlreadyExistsException()
        
        # hashing password
        hashed_pw = hash_password(user_data.password)

        #Il primo utente per ogni ruolo viente attivato automaticamente
        utenti_con_ruolo = await UserRepository.get_all_with_role(db, user_data.ruolo)
        primo_per_ruolo = len(utenti_con_ruolo) == 0

        # entity/Model
        new_user = User(
            id = uuid.uuid4(),
            name=user_data.name,
            email=user_data.email,
            hashed_password=hashed_pw,
            attivo=primo_per_ruolo, # True solo se è il primo del suo ruolo
            ruolo=user_data.ruolo
        )
        try:
            return await UserRepository.create(db, new_user)
        except IntegrityError:
            await db.rollback()
            raise EmailAlreadyExistsException()
        
    @staticmethod
    def check_name(name: str):

        # consenti lettere, spazi, apostrofo e trattino
        pattern = r"^[a-zA-ZÀ-ÖØ-öø-ÿ\s'-]+$"

        if not re.match(pattern, name):
            raise InvalidNameException()
        
    @staticmethod
    def check_password_strength(password: str):
        has_upper = any(char.isupper() for char in password)
        has_digit = any(char.isdigit() for char in password)
        has_lower = any(char.islower() for char in password)

        if not has_lower:
            raise InvalidCredentials()
        
        if not has_upper:
            raise InvalidCredentials()

        if not has_digit:
            raise InvalidCredentials()
    
    @staticmethod
    async def get_user_by_email(email: str, db:AsyncSession):
        user = await UserRepository.get_by_email(db, email)

        if not user:
            raise UserNotFoundException()
        
        return user
    
    @staticmethod
    async def get_users(db: AsyncSession):
        return await UserRepository.get_all(db)
    
    @staticmethod
    async def get_users_with_role(role: ruolo, db: AsyncSession):
        return await UserRepository.get_all_with_role(db, role)

    @staticmethod
    async def authenticate_user(login_data: LoginRequest, db: AsyncSession):
        user = await UserRepository.get_by_email(db, login_data.email)
        
        if user is None:
            raise UserNotFoundException()
        
        if not cast(bool, user.attivo):
            raise UserNotActive()
        
        if not user or not verify_password(login_data.password, cast(str, user.hashed_password)):
            raise InvalidCredentials()
        
        # Generiamo il token includendo email e ruolo (opzionale)
        token_data = {"sub": user.email, "role": user.ruolo}
        token = create_access_token(token_data)
        
        return {"access_token": token, "token_type": "bearer"}, user
    
    @staticmethod
    async def get_users_by_role(
        role: ruolo,
        db: AsyncSession
    ):
        return await UserRepository.get_by_role(
            db,
            role
        )
    
    @staticmethod
    async def get_user_by_id(
        user_id,
        db: AsyncSession
    ):
        user = await UserRepository.get_by_id(
            db,
            user_id
        )
        if not user:
            raise UserNotFoundException()
        return user
    
    @staticmethod
    async def active_user(
        user_id,
        db: AsyncSession
    ):
        try:
            user = await UserRepository.active_new_user_by_id(db, user_id)
        except ValueError:
            raise UserAlreadyActive()
        if user is None:
            raise UserNotFoundException()
        return user

    @staticmethod
    async def get_all(db: AsyncSession):
        return await UserRepository.get_all(db)

