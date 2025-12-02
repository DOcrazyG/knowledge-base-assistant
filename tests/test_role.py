import pytest
from httpx import AsyncClient

from app.main import app

base_url = "http://localhost:8000"


@pytest.fixture
def async_backend():
    return "asyncio"


async def fetch_access_token():
    async with AsyncClient(app=app, base_url=base_url) as client:
        response = await client.post(
            "/login/token",
            data={"username": "admin", "password": "123456"},
        )
        return response.json()["access_token"]


@pytest.mark.asyncio
async def test_read_roles():
    access_token = await fetch_access_token()
    async with AsyncClient(app=app, base_url=base_url) as client:
        response = await client.get(
            "/roles/",
            headers={
                "Authorization": f"Bearer {access_token}",
                "accept": "application/json",
            },
        )
        assert response.status_code == 200
        info = response.json()
        assert isinstance(info, list)
        for role in info:
            assert "id" in role
            assert "name" in role
            assert "permissions" in role


@pytest.mark.asyncio
async def test_create_role():
    access_token = await fetch_access_token()
    async with AsyncClient(app=app, base_url=base_url) as client:
        response = await client.post(
            "/roles/",
            json={"name": "test_role"},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        assert "name" in response.json()
        assert "permissions" in response.json()
        assert response.json()["name"] == "test_role"


@pytest.mark.asyncio
async def test_read_role_by_id():
    access_token = await fetch_access_token()
    async with AsyncClient(app=app, base_url=base_url) as client:
        # First create a role to ensure we have something to read
        create_response = await client.post(
            "/roles/",
            json={
                "name": "temp_role",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        role_id = create_response.json()["id"]

        # Read the role by ID
        response = await client.get(
            f"/roles/{role_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "accept": "application/json",
            },
        )
        assert response.status_code == 200
        info = response.json()
        assert "name" in info
        assert "permissions" in response.json()
        assert info["name"] == "temp_role"


@pytest.mark.asyncio
async def test_update_role():
    access_token = await fetch_access_token()
    async with AsyncClient(app=app, base_url=base_url) as client:
        # First create a role to update
        create_response = await client.post(
            "/roles/",
            json={"name": "role_to_update"},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        role_id = create_response.json()["id"]

        # Update the role
        response = await client.put(
            f"/roles/{role_id}",
            json={"name": "updated_role"},
            headers={
                "Authorization": f"Bearer {access_token}",
                "accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        assert response.status_code == 200
        info = response.json()
        assert "name" in info
        assert "permissions" in info
        assert info["name"] == "updated_role"


@pytest.mark.asyncio
async def test_delete_role():
    access_token = await fetch_access_token()
    async with AsyncClient(app=app, base_url=base_url) as client:
        # First create a role to delete
        create_response = await client.post(
            "/roles/",
            json={"name": "role_to_delete"},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        role_id = create_response.json()["id"]

        # Delete the role
        response = await client.delete(
            f"/roles/{role_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "accept": "application/json",
            },
        )
        assert response.status_code == 200
