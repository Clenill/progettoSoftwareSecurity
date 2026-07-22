from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import User
from app.enum.ruolo import ruolo

class UserRepository:

    @staticmethod
    async def get_by_email(db: AsyncSession, email:str):
        result = await db.execute(
            select(User).where(User.email == email)
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_with_role(db: AsyncSession, role: ruolo):
        result = await db.execute(
            select(User).where(User.ruolo == role)
        )
        return result.scalars().all()

    @staticmethod
    async def get_all_active_with_role(db: AsyncSession, role: ruolo):
        result = await db.execute(
            select(User).where(User.ruolo == role, User.attivo == True)
        )
        return result.scalars().all()
    
    @staticmethod
    async def create(db: AsyncSession, user: User):
        db.add(user)

        await db.commit()
        await db.refresh(user)

        return user
    
    @staticmethod
    async def get_all(db: AsyncSession):
        result = await db.execute(select(User))
        return result.scalars().all()

    @staticmethod
    async def get_all_active(db: AsyncSession):
        result = await db.execute(select(User).where(User.attivo == True))
        return result.scalars().all()
    
    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        user_id
    ):
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_role(
        db: AsyncSession,
        role: ruolo
    ):
        result = await db.execute(
            select(User).where(User.ruolo == role)
        )
        return result.scalars().all()
    
    @staticmethod
    async def active_new_user_by_id(
        db: AsyncSession,
        user_id
    ):
        user = await UserRepository.get_by_id(db, user_id)
        if user != None:
            if user.attivo:
                raise ValueError('utente già attivo')
            user.attivo = True
            await db.commit()
            await db.refresh(user)
        return user

