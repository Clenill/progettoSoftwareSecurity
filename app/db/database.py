from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv
from app.core.config import ISOLATION_LEVEL, DB_TIMEOUT_SECONDS

load_dotenv()

DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{os.getenv('DB_USERNAME')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)

engine = create_async_engine(
    DATABASE_URL, 
    echo=True, 
    poolclass=NullPool, 
    connect_args={
        "timeout": DB_TIMEOUT_SECONDS, 
        "command_timeout": DB_TIMEOUT_SECONDS, 
        "server_settings": {
            "statement_timeout": f"{DB_TIMEOUT_SECONDS * 1000}"
        }
    }
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with SessionLocal() as session:
        yield session
