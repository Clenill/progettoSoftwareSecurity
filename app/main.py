from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHttpException
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

    await public_monitor.bg_cleanup()
    await admin_monitor.bg_cleanup()

    print("\n===== SERVER AVVIATO =====")
    print("Swagger Docs: https://127.0.0.1:8443/docs")
    print("ReDoc: https://127.0.0.1:8443/redoc")
    print("Pagina HOME: https://127.0.0.1:8443/")
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

    if request.url.path.startswith(("/api", "/auth", "/visit", "/admin")):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status_code": exc.status_code,
                "error_code": exc.error_code,
                "detail": exc.detail
            },
            headers=exc.headers or None
        )

    return templates.TemplateResponse(
        request=request, 
        name="pagina_errore.html",
        status_code=exc.status_code,
        context= {
            "status_code" : exc.status_code,
            "content" : {
                "status_code": exc.status_code,
                "error_code": exc.error_code,
                "detail": exc.detail
            }
        }, 
        headers=exc.headers or None
    )

@app.exception_handler(StarletteHttpException)
async def app_exception_handler_due(
    request: Request,
    exc: StarletteHttpException
):

    headers = exc.headers if hasattr(exc, 'headers') else dict()

    if request.url.path.startswith(("/api", "/auth", "/visit", "/admin")):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status_code": exc.status_code,
                "detail": exc.detail
            },
            headers=headers
        )

    return templates.TemplateResponse(
        request=request, 
        name="pagina_errore.html",
        status_code=exc.status_code,
        context= {
            "status_code" : exc.status_code,
            "content" : {
                "status_code": exc.status_code,
                "detail": exc.detail
            }
        }, 
        headers=headers
    )


@app.exception_handler(HTTPException)
async def app_exception_handler_http(
    request: Request,
    exc: HTTPException
):
    
    headers = exc.headers if hasattr(exc, 'headers') else dict()

    if request.url.path.startswith(("/api", "/auth", "/visit", "/admin")):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status_code": exc.status_code,
                "detail": exc.detail
            },
            headers=headers
        )

    return templates.TemplateResponse(
        request=request, 
        name="pagina_errore.html",
        status_code=exc.status_code,
        context= {
            "status_code" : exc.status_code,
            "content" : {
                "status_code": exc.status_code,
                "detail": exc.detail
            }
        }, 
        headers=headers
    )
