from fastapi import FastAPI, Request, Response, Depends
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import engine
from app.db.models import Base
from app.api.routes import router   
from pathlib import Path
from app.api.ui_routes import ui_router
from app.core.exceptions import AppException
from app.core.config import MAX_REQUESTS, CLEANUP_INTERVAL_SECONDS
from app.core.logging import log_request
from app.core.re_monitor import public_monitor, admin_monitor
from app.api.auth_routes import router as auth_router
from app.api.visit_routes import router as visit_router
from app.api.admin_routes import router as admin_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await public_monitor.bg_cleanup()
    await admin_monitor.bg_cleanup()

    print("\n===== SERVER AVVIATO =====")
    print("Swagger Docs: http://127.0.0.1:8000/docs")
    print("ReDoc: http://127.0.0.1:8000/redoc")
    print("==========================\n")

    yield

    # Shutdon
    print("Server spento")

# Configurazione Jinja2
BASE_PATH = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_PATH / "templates"))

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware, 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    return await log_request(request, call_next)

# Configura la cartella dei file statici
app.mount("/css", StaticFiles(directory="app/css"), name="static")

app.mount("/images", StaticFiles(directory="app/images"), name="images")

app.mount("/js", StaticFiles(directory="app/js"), name="static")

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

    headers = exc.headers if hasattr(exc, 'headers') else dict()
    return templates.TemplateResponse(
        request=request, 
        name="pagina_errore.html",
        context= {
            "status_code" : exc.status_code,
            "content" : {
                "status_code": exc.status_code,
                "error_code": exc.error_code,
                "detail": exc.detail
            }
        }, 
        headers=headers
    )


