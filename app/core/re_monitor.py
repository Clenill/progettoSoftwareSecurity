
import asyncio
import time
from collections import defaultdict
from fastapi import Request
from app.core.config import MAX_REQUESTS, CLEANUP_INTERVAL_SECONDS
from app.core.logging import logger
from app.core.security import get_client_metadata, sanitize_str
from app.core.exceptions import RequestLimitExceededException
from app.enum.ruolo import ruolo

class RuntimeEnforcementMonitor:
    """Applica rate limiting alle richieste degli utenti"""

    def __init__(self, max_requests: int = 5, delta_seconds: int = 10):
        """max_requests: Numero massimo di richieste eseguibili da un utente.
           delta_seconds: Intervallo di controllo del numero di richieste.
        """
        self.max_requests = max_requests
        self.delta_seconds = delta_seconds
        self._history = defaultdict(list)

    async def bg_cleanup(self):
        """Avvia il task di pulizia in background"""
        asyncio.create_task(self._clean_expired_records())

    async def _clean_expired_records(self):
        """Pulisce i record della lista più vecchi dell'intervallo scelto"""
        while True:
            await asyncio.sleep(self.delta_seconds)
            now = time.perf_counter()
            for client in list(self._history.keys()):
                # Ricalcola la lista di richieste nella finestra considerata
                self._history[client] = [t for t in self._history[client] if t > (now - self.delta_seconds)]
                # Elimina le liste vuote
                if not self._history[client]:
                    del self._history[client]

    async def __call__(self, request: Request):
        """Esegue il controllo del numero di richieste nella storia dell'utente"""
        ip, email, role = get_client_metadata(request)
        path = sanitize_str(request.url.path)
        method = sanitize_str(request.method)

        now = time.perf_counter()
        # Calcola la lista di richieste nella finestra considerata
        self._history[ip] = [t for t in self._history[ip] if t > (now - self.delta_seconds)]

        if len(self._history[ip]) >= self.max_requests:
            context_logger = logger.bind(
                ip=ip, 
                caller=email, 
                role=role, 
                method=method, 
                path=path
            )
            context_logger.warning(f"{ip} EXCEEDED LIMIT ON {method} {path}")
            
            raise RequestLimitExceededException(self.delta_seconds)

        self._history[ip].append(now)

public_monitor = RuntimeEnforcementMonitor(
    max_requests=MAX_REQUESTS, 
    delta_seconds=CLEANUP_INTERVAL_SECONDS
)

admin_monitor = RuntimeEnforcementMonitor(
    max_requests=2 * MAX_REQUESTS, 
    delta_seconds=CLEANUP_INTERVAL_SECONDS
)

