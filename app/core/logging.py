
import time
from os.path import join
from loguru import logger
from fastapi import Request
from app.core.security import sanitize_str, get_client_metadata
from app.core.config import MAX_LOG_FILE_SIZE, LOG_RETENTION, LOG_PATH

logger.remove()
logger.add(
    join(LOG_PATH, "system.log"), 
    rotation=MAX_LOG_FILE_SIZE, 
    retention=LOG_RETENTION, 
    compression="zip", 
    serialize=True
)

async def log_request(request: Request, call_next):
    ip, email, role = get_client_metadata(request)
    path = sanitize_str(request.url.path)
    method = sanitize_str(request.method)
    start_time = time.perf_counter()

    response = await call_next(request)

    end_time = time.perf_counter()
    context_logger = logger.bind(
        ip=ip, 
        caller=email, 
        role=role, 
        method=method, 
        path=path, 
        status_code=response.status_code, 
        duration=(end_time - start_time) * 1000
    )
    context_logger.info(f"HTTP {ip} {method} {path}")

    return response

