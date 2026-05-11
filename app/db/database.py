from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
import os
from dotenv import load_dotenv

load_dotenv()
with open('/run/secrets/db_password', 'r') as f:
    db_password = f.read()

DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{os.getenv('DB_USERNAME')}:"
    f"{db_password}@"
    f"{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)

del db_password
engine = create_async_engine(DATABASE_URL, echo=True)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with SessionLocal() as session:
        yield session
