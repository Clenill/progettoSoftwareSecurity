# tests/test_sql_injection.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.re_monitor import public_monitor, admin_monitor

@pytest.fixture(autouse=True)
def pulisci_monitor():
    public_monitor._history.clear()
    admin_monitor._history.clear()
    yield
    public_monitor._history.clear()
    admin_monitor._history.clear()

PAYLOAD_SQL = [
    "' OR '1'='1",
    "'; DROP TABLE users; --",
    "' UNION SELECT * FROM users --",
    "admin'--",
    "' OR 1=1--",
    "\" OR \"1\"=\"1",
]


@pytest.mark.asyncio
async def test_sql_injection_login_email():
    """Payload SQL injection nel campo email del login non deve autenticare."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for payload in PAYLOAD_SQL:
            r = await client.post("/auth/login", json={
                "email": payload,
                "password": "qualsiasi"
            })
            assert r.status_code in (400, 401, 422), \
                f"Payload '{payload}' ha restituito {r.status_code} — possibile SQLi"
            assert r.status_code != 200, \
                f"Payload SQLi '{payload}' ha effettuato il login!"
            assert r.status_code != 500, \
                f"Payload SQLi '{payload}' ha causato un errore 500 — il server è crashato"


@pytest.mark.asyncio
async def test_sql_injection_login_password():
    """Payload SQL injection nel campo password non deve autenticare."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for payload in PAYLOAD_SQL:
            r = await client.post("/auth/login", json={
                "email": "test@test.com",
                "password": payload
            })
            assert r.status_code != 200, \
                f"Payload SQLi in password '{payload}' ha effettuato il login!"
            assert r.status_code != 500, \
                f"Payload SQLi in password '{payload}' ha causato un errore 500"


@pytest.mark.asyncio
async def test_sql_injection_registrazione_nome():
    """Payload SQL injection nel campo nome durante la registrazione."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for payload in PAYLOAD_SQL:
            r = await client.post("/auth/register", json={
                "name": payload,
                "email": f"test_{hash(payload)}@test.com",
                "password": "Password123",
                "ruolo": "utente"
            })
            assert r.status_code != 500, \
                f"Payload SQLi nel nome '{payload}' ha causato un errore 500"


@pytest.mark.asyncio
async def test_sql_injection_registrazione_email():
    """Payload SQL injection nel campo email durante la registrazione."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for payload in PAYLOAD_SQL:
            r = await client.post("/auth/register", json={
                "name": "Test User",
                "email": payload,
                "password": "Password123",
                "ruolo": "utente"
            })
            assert r.status_code in (400, 422), \
                f"Email SQLi '{payload}' non rifiutata: {r.status_code}"
            assert r.status_code != 500, \
                f"Payload SQLi nell'email '{payload}' ha causato un errore 500"


@pytest.mark.asyncio
async def test_sql_injection_uuid_visita():
    """UUID malformato o con payload SQL nella rotta visita."""
    payloads_uuid = [
        "' OR '1'='1",
        "1; DROP TABLE visits;--",
        "00000000-0000-0000-0000-000000000000' OR '1'='1",
    ]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for payload in payloads_uuid:
            r = await client.get(f"/visit/dettagliovisita/{payload}")
            assert r.status_code in (400, 401, 403, 404, 422), \
                f"UUID SQLi '{payload}' ha restituito {r.status_code}"
            assert r.status_code != 500, \
                f"UUID SQLi '{payload}' ha causato un errore 500"