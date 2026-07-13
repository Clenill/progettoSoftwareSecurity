# tests/test_autenticazione.py
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


# ── Rotte protette senza token ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_rotta_paziente_senza_token():
    """Accesso a rotta paziente senza token deve restituire 401 o 307."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/utente/visite")
        assert r.status_code in (401, 307, 403), \
            f"Rotta paziente accessibile senza token: {r.status_code}"

@pytest.mark.asyncio
async def test_rotta_medico_senza_token():
    """Accesso a rotta medico senza token deve essere bloccato."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/dashboard/staff")
        assert r.status_code in (401, 307, 403), \
            f"Rotta medico accessibile senza token: {r.status_code}"

@pytest.mark.asyncio
async def test_rotta_admin_senza_token():
    """Accesso a rotta admin senza token deve essere bloccato."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/dashboard/authority")
        assert r.status_code in (401, 307, 403), \
            f"Rotta admin accessibile senza token: {r.status_code}"


# ── Token invalidi ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_token_invalido_stringa_casuale():
    """Un token completamente inventato deve essere rifiutato."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        client.cookies.set("access_token", "Bearer token_falso_12345")
        r = await client.get("/utente/visite")
        assert r.status_code in (401, 307, 403), \
            f"Token falso accettato: {r.status_code}"

@pytest.mark.asyncio
async def test_token_malformato_senza_bearer():
    """Token senza prefisso Bearer deve essere rifiutato."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        client.cookies.set("access_token", "solounastringacasuale")
        r = await client.get("/utente/visite")
        assert r.status_code in (401, 307, 403), \
            f"Token malformato accettato: {r.status_code}"

@pytest.mark.asyncio
async def test_token_jwt_firma_errata():
    """JWT con firma errata deve essere rifiutato."""
    # JWT valido strutturalmente ma firmato con chiave sbagliata
    jwt_falso = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"  # header
        ".eyJzdWIiOiJ0ZXN0QHRlc3QuY29tIiwicm9sZSI6InV0ZW50ZSJ9"  # payload
        ".firma_completamente_sbagliata"  # firma invalida
    )
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        client.cookies.set("access_token", f"Bearer {jwt_falso}")
        r = await client.get("/utente/visite")
        assert r.status_code in (401, 307, 403), \
            f"JWT con firma errata accettato: {r.status_code}"


# ── Accesso cross-ruolo ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_paziente_non_accede_a_rotta_medico():
    """Un paziente autenticato non deve accedere a rotte riservate al medico."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Login come paziente
        r = await client.post("/auth/login", json={
            "email": "paziente@example.com",
            "password": "password_paziente"
        })
        if r.status_code != 200:
            pytest.skip("Credenziali paziente non disponibili nel DB di test")

        r = await client.get("/dashboard/staff")
        assert r.status_code in (401, 307, 403), \
            f"Paziente ha acceduto a rotta medico: {r.status_code}"

@pytest.mark.asyncio
async def test_paziente_non_accede_a_rotta_admin():
    """Un paziente autenticato non deve accedere a rotte admin."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/auth/login", json={
            "email": "paziente@example.com",
            "password": "password_paziente"
        })
        if r.status_code != 200:
            pytest.skip("Credenziali paziente non disponibili nel DB di test")

        r = await client.get("/dashboard/authority")
        assert r.status_code in (401, 307, 403), \
            f"Paziente ha acceduto a rotta admin: {r.status_code}"

@pytest.mark.asyncio
async def test_medico_non_accede_a_rotta_admin():
    """Un medico autenticato non deve accedere a rotte admin."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/auth/login", json={
            "email": "medico@example.com",
            "password": "password_medico"
        })
        if r.status_code != 200:
            pytest.skip("Credenziali medico non disponibili nel DB di test")

        r = await client.get("/dashboard/authority")
        assert r.status_code in (401, 307, 403), \
            f"Medico ha acceduto a rotta admin: {r.status_code}"