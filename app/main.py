from fastapi import FastAPI
from app.api.routes import router
from contextlib import asynccontextmanager

from app.db.database import engine
from app.db.models import Base
from app.api.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("\n===== SERVER AVVIATO =====")
    print("Home: http://127.0.0.1:8000/api/")
    print("Swagger Docs: http://127.0.0.1:8000/docs")
    print("ReDoc: http://127.0.0.1:8000/redoc")
    print("==========================\n")

    yield

    # Shutdon
    print("Server spento")

app = FastAPI(lifespan=lifespan)

app.include_router(router, prefix="/api")