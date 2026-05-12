import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.db.models import User
from app.models.schemas import UserCreate
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password
from app.core.exceptions import (
    UserNotFoundException,
    EmailAlreadyExistsException,
    PasswordTooLongException
)

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