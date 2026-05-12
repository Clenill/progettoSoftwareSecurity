from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import User

class UserRepository:

    @staticmethod
    async def get_by_email(db: AsyncSession, email:str):
        result = await db.execute(
            select(User).where(User.email == email)
        )

        return result.scalar_one_or_none()
    
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
    
    
