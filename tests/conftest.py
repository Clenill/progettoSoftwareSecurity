import pytest_asyncio
import pytest

from app.db.database import engine
from app.core.security import hash_password
from app.enum.ruolo import ruolo
from app.db.models import User
from app.db.database import SessionLocal


@pytest_asyncio.fixture(scope="session", autouse=True)
async def cleanup_database():
    yield

    await engine.dispose()

@pytest.fixture
async def crea_paziente_test():

    async with SessionLocal() as db:

        user = User(
            name="Test Paziente",
            email="paziente@test.com",
            hashed_password=hash_password("Password123!"),
            attivo=True,
            ruolo=ruolo.PAZIENTE
        )

        db.add(user)
        await db.commit()

        yield user


        await db.delete(user)
        await db.commit()