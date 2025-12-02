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
async def test_create_permission():
    access_token = await fetch_access_token()
    async with AsyncClient(app=app, base_url=base_url) as client:
        response = await client.post(
            "/permissions/",
            json={
                "name": "test:permission",
                "description": "Test permission for unit testing"
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        assert "name" in response.json()
        assert "description" in response.json()
        assert response.json()["name"] == "test:permission"


@pytest.mark.asyncio
async def test_read_permissions():
    access_token = await fetch_access_token()
    async with AsyncClient(app=app, base_url=base_url) as client:
        response = await client.get(
            "/permissions/",
            headers={
                "Authorization": f"Bearer {access_token}",
                "accept": "application/json",
            },
        )
        assert response.status_code == 200
        info = response.json()
        assert isinstance(info, list)


@pytest.mark.asyncio
async def test_read_permission_by_id():
    access_token = await fetch_access_token()
    async with AsyncClient(app=app, base_url=base_url) as client:
        # First create a permission to ensure we have something to read
        create_response = await client.post(
            "/permissions/",
            json={
                "name": "temp:permission",
                "description": "Temporary permission for reading test"
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        permission_id = create_response.json()["id"]
        
        # Read the permission by ID
        response = await client.get(
            f"/permissions/{permission_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "accept": "application/json",
            },
        )
        assert response.status_code == 200
        info = response.json()
        assert "name" in info
        assert "description" in info
        assert info["name"] == "temp:permission"


@pytest.mark.asyncio
async def test_update_permission():
    access_token = await fetch_access_token()
    async with AsyncClient(app=app, base_url=base_url) as client:
        # First create a permission to update
        create_response = await client.post(
            "/permissions/",
            json={
                "name": "permission:to:update",
                "description": "Permission to be updated"
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        permission_id = create_response.json()["id"]
        
        # Update the permission
        response = await client.put(
            f"/permissions/{permission_id}",
            json={
                "name": "permission:updated",
                "description": "Updated permission description"
            },
            headers={
                "Authorization": f"Bearer {access_token}",
                "accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        assert response.status_code == 200
        info = response.json()
        assert info["name"] == "permission:updated"
        assert info["description"] == "Updated permission description"


@pytest.mark.asyncio
async def test_delete_permission():
    access_token = await fetch_access_token()
    async with AsyncClient(app=app, base_url=base_url) as client:
        # First create a permission to delete
        create_response = await client.post(
            "/permissions/",
            json={
                "name": "permission:to:delete",
                "description": "Permission to be deleted"
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        permission_id = create_response.json()["id"]
        
        # Delete the permission
        response = await client.delete(
            f"/permissions/{permission_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "accept": "application/json",
            },
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_assign_permission_to_role():
    access_token = await fetch_access_token()
    async with AsyncClient(app=app, base_url=base_url) as client:
        # Create a permission
        perm_response = await client.post(
            "/permissions/",
            json={
                "name": "assign:test",
                "description": "Permission for assignment test"
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        permission_id = perm_response.json()["id"]
        
        # Get an existing role (use role ID 1 which should be admin)
        role_id = 1
        
        # Assign permission to role
        response = await client.post(
            f"/permissions/{role_id}/permissions/{permission_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "accept": "application/json",
            },
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_remove_permission_from_role():
    access_token = await fetch_access_token()
    async with AsyncClient(app=app, base_url=base_url) as client:
        # Create a permission
        perm_response = await client.post(
            "/permissions/",
            json={
                "name": "remove:test",
                "description": "Permission for removal test"
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        permission_id = perm_response.json()["id"]
        
        # Get an existing role (use role ID 1 which should be admin)
        role_id = 1
        
        # First assign permission to role
        await client.post(
            f"/permissions/{role_id}/permissions/{permission_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        
        # Remove permission from role
        response = await client.delete(
            f"/permissions/{role_id}/permissions/{permission_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "accept": "application/json",
            },
        )
        assert response.status_code == 200