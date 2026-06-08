
import pytest 
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT
from app.db.database import get_db
from app.db.models import Base
from app.main import app

TEST_DATABASE_URL = (
    "postgresql+asyncpg://"
    f"{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/testdb"
)

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_test_db():
    """Crea e distrugge le tabelle del database di test"""
    async with test_engine.begin() as c:
        await c.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as c:
        await c.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with test_engine.connect() as connection:
        transaction = await connection.begin()
        async with TestingSessionLocal(bind=connection) as session:
            yield session
            await session.close()
        await transaction.rollback()

@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """Sostituisce get_db e restituisce il client di test"""
    async def _get_db():
        yield db_session
    app.dependency_overrides[get_db] = _get_db
    async with AsyncClient(transport=ASGITransport(app=app)) as async_client:
        yield async_client
    app.dependency_overrides.clear()
