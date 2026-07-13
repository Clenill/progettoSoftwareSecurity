import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_register_email_non_valida():

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:

        response = await client.post(
            "/auth/register",
            json={
                "name": "Mario Rossi",
                "email": "email_sbagliata",
                "password": "Password123",
                "ruolo": "utente"
            }
        )

        assert response.status_code != 500
        assert response.status_code == 422



@pytest.mark.asyncio
async def test_register_nome_troppo_corto():

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:

        response = await client.post(
            "/auth/register",
            json={
                "name": "A",
                "email": "mario@test.it",
                "password": "Password123",
                "ruolo": "utente"
            }
        )

        assert response.status_code != 500
        assert response.status_code == 422



@pytest.mark.asyncio
async def test_register_password_troppo_lunga():

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:

        response = await client.post(
            "/auth/register",
            json={
                "name": "Mario Rossi",
                "email": "lungapassword@test.it",
                "password": "A" * 1000,
                "ruolo": "utente"
            }
        )

        assert response.status_code != 500
        assert response.status_code == 422



@pytest.mark.asyncio
async def test_register_ruolo_non_valido():

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:

        response = await client.post(
            "/auth/register",
            json={
                "name": "Mario Rossi",
                "email": "ruolo@test.it",
                "password": "Password123",
                "ruolo": "superadmin"
            }
        )

        assert response.status_code != 500
        assert response.status_code == 422



@pytest.mark.asyncio
async def test_register_body_vuoto():

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:

        response = await client.post(
            "/auth/register",
            json={}
        )

        assert response.status_code != 500
        assert response.status_code == 422