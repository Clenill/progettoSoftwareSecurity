from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles

from app.db.database import engine
from app.db.models import Base
from app.api.routes import router            
from app.api.ui_routes import ui_router
from app.core.exceptions import AppException
from app.api.auth_routes import router as auth_router
from app.api.visit_routes import router as visit_router
from app.api.admin_routes import router as admin_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("\n===== SERVER AVVIATO =====")
    print("Swagger Docs: http://127.0.0.1:8000/docs")
    print("ReDoc: http://127.0.0.1:8000/redoc")
    print("==========================\n")

    yield

    # Shutdon
    print("Server spento")

app = FastAPI(lifespan=lifespan)

# Configura la cartella dei file statici
app.mount("/css", StaticFiles(directory="app/css"), name="static")

app.mount("/images", StaticFiles(directory="app/images"), name="images")

app.include_router(ui_router)

app.include_router(router, prefix="/api")

app.include_router(auth_router)

app.include_router(visit_router)

app.include_router(admin_router)

@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request,
    exc: AppException
):

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "detail": exc.detail
        }
    )