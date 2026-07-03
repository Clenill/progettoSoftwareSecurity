# tests/test_rate_limit.py
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.re_monitor import public_monitor, admin_monitor
from app.core.config import MAX_REQUESTS


def reset_monitors():
    """Pulisce la storia delle richieste tra un test e l'altro."""
    public_monitor._history.clear()
    admin_monitor._history.clear()


@pytest.fixture(autouse=True)
def pulisci_monitor():
    """Fixture che resetta i monitor prima di ogni test."""
    reset_monitors()
    yield
    reset_monitors()


@pytest.mark.asyncio
async def test_rate_limit_pubblico_non_scatta_sotto_soglia():
    """Richieste sotto il limite non devono essere bloccate."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        for _ in range(MAX_REQUESTS - 1):
            r = await client.get("/")
            assert r.status_code != 429, \
                f"Rate limit scattato troppo presto alla richiesta {_ + 1}"


@pytest.mark.asyncio
async def test_rate_limit_pubblico_scatta_alla_soglia():
    """Alla richiesta MAX_REQUESTS+1 deve restituire 429."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        for _ in range(MAX_REQUESTS):
            await client.get("/")

        # La richiesta successiva deve essere bloccata
        r = await client.get("/")
        assert r.status_code == 429, \
            f"Atteso 429, ricevuto {r.status_code}"


@pytest.mark.asyncio
async def test_rate_limit_risposta_contiene_retry_after():
    """La risposta 429 deve contenere l'header Retry-After."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        for _ in range(MAX_REQUESTS):
            await client.get("/")

        r = await client.get("/")
        assert r.status_code == 429
        assert "retry-after" in r.headers, \
            "Header Retry-After mancante nella risposta 429"


@pytest.mark.asyncio
async def test_rate_limit_admin_soglia_doppia():
    """Il monitor admin ha soglia doppia rispetto al pubblico."""
    from app.core.re_monitor import admin_monitor
    from app.core.exceptions import RequestLimitExceededException
    from unittest.mock import MagicMock
    from starlette.datastructures import Headers
    from app.core.security import get_client_metadata

    mock_request = MagicMock()
    mock_request.headers = Headers({"x-forwarded-for": "10.0.0.1"})
    mock_request.client.host = "10.0.0.1"
    mock_request.url.path = "/dashboard/authority"
    mock_request.method = "GET"
    mock_request.state = MagicMock()
    mock_request.cookies = {}

    admin_monitor._history.clear()

    # Verifica che l'IP venga letto correttamente
    ip, _, _ = get_client_metadata(mock_request)
    assert ip == "10.0.0.1", f"IP letto male: {ip}"

    # Fino a MAX_REQUESTS * 2 - 1 non deve bloccare
    for i in range(MAX_REQUESTS * 2):
        try:
            await admin_monitor(mock_request)
        except RequestLimitExceededException:
            pytest.fail(f"Admin monitor ha bloccato troppo presto alla richiesta {i + 1}")

    # La richiesta successiva (la numero MAX_REQUESTS * 2 + 1) deve essere bloccata
    with pytest.raises(RequestLimitExceededException):
        await admin_monitor(mock_request)


@pytest.mark.asyncio
async def test_rate_limit_reset_dopo_intervallo():
    """Dopo l'intervallo di cleanup le richieste devono essere nuovamente accettate."""
    from app.core.config import CLEANUP_INTERVAL_SECONDS

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        # Supera il limite
        for _ in range(MAX_REQUESTS):
            await client.get("/")
        r = await client.get("/")
        assert r.status_code == 429

        # Aspetta la scadenza della finestra
        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS + 1)

        # Ora deve essere nuovamente accettata
        r = await client.get("/")
        assert r.status_code != 429, \
            "Le richieste non sono state sbloccate dopo l'intervallo"


@pytest.mark.asyncio
async def test_rate_limit_ip_diversi_non_interferiscono():
    """IP diversi hanno contatori indipendenti."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Forwarded-For": "1.2.3.4"}
    ) as client_a:
        for _ in range(MAX_REQUESTS):
            await client_a.get("/")
        r = await client_a.get("/")
        assert r.status_code == 429

    # IP diverso — non deve essere bloccato
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Forwarded-For": "9.8.7.6"}
    ) as client_b:
        r = await client_b.get("/")
        assert r.status_code != 429, \
            "IP diverso bloccato per colpa di un altro IP"