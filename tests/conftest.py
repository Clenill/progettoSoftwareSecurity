import pytest_asyncio
from app.db.database import engine


@pytest_asyncio.fixture(scope="session", autouse=True)
async def cleanup_database():
    yield

    await engine.dispose()