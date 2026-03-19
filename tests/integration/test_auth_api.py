import pytest


@pytest.mark.asyncio
async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "operativa" in data["message"]


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["status"] == "healthy"


@pytest.mark.asyncio
async def test_register_user(client):
    response = await client.post("/api/auth/register", json={
        "username": "newuser",
        "email": "new@example.com",
        "password": "securepass123",
        "full_name": "New User",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["user"]["username"] == "newuser"


@pytest.mark.asyncio
async def test_register_duplicate_username(client):
    # Primer registro
    await client.post("/api/auth/register", json={
        "username": "duplicate",
        "email": "dup1@example.com",
        "password": "securepass123",
    })
    # Segundo registro con mismo username
    response = await client.post("/api/auth/register", json={
        "username": "duplicate",
        "email": "dup2@example.com",
        "password": "securepass123",
    })
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_user(client, test_user):
    response = await client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "testpass123",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]


@pytest.mark.asyncio
async def test_login_wrong_password(client, test_user):
    response = await client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "wrongpass",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client, auth_headers):
    response = await client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["username"] == "testuser"


@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client):
    response = await client.get("/api/portfolios")
    assert response.status_code == 401
