import pytest


@pytest.mark.asyncio
async def test_create_portfolio(client, auth_headers):
    response = await client.post("/api/portfolios", json={
        "name": "Test Portfolio",
        "description": "Un portfolio de prueba",
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Test Portfolio"
    assert "id" in data["data"]


@pytest.mark.asyncio
async def test_list_portfolios(client, auth_headers):
    # Crear uno primero
    await client.post("/api/portfolios", json={"name": "Port 1"}, headers=auth_headers)
    await client.post("/api/portfolios", json={"name": "Port 2"}, headers=auth_headers)

    response = await client.get("/api/portfolios", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["total"] >= 2


@pytest.mark.asyncio
async def test_get_portfolio(client, auth_headers):
    # Crear
    create_resp = await client.post("/api/portfolios", json={"name": "Get Me"}, headers=auth_headers)
    portfolio_id = create_resp.json()["data"]["id"]

    # Obtener
    response = await client.get(f"/api/portfolios/{portfolio_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Get Me"


@pytest.mark.asyncio
async def test_update_portfolio(client, auth_headers):
    create_resp = await client.post("/api/portfolios", json={"name": "Old Name"}, headers=auth_headers)
    portfolio_id = create_resp.json()["data"]["id"]

    response = await client.put(f"/api/portfolios/{portfolio_id}", json={
        "name": "New Name",
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_portfolio(client, auth_headers):
    create_resp = await client.post("/api/portfolios", json={"name": "Delete Me"}, headers=auth_headers)
    portfolio_id = create_resp.json()["data"]["id"]

    response = await client.delete(f"/api/portfolios/{portfolio_id}", headers=auth_headers)
    assert response.status_code == 200

    # Verificar que no existe
    get_resp = await client.get(f"/api/portfolios/{portfolio_id}", headers=auth_headers)
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_portfolio(client, auth_headers):
    response = await client.get(
        "/api/portfolios/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert response.status_code == 404
