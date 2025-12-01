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
async def test_create_user():
    access_token = await fetch_access_token()
    async with AsyncClient(app=app, base_url=base_url) as client:
        response = await client.post(
            "/users/register",
            json={
                "username": "test01",
                "email": "test01@gmail.com",
                "password": "test01",
                "is_active": True,
                "role_id": 1,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        assert "is_active" in response.json()
        assert "role_id" in response.json()


@pytest.mark.asyncio
async def test_read_users():
    access_token = await fetch_access_token()
    async with AsyncClient(app=app, base_url=base_url) as client:
        response = await client.get(
            "/users/",  # FastAPI中，/users和 /users/被视为两个完全不同的端点，因此当请求/users时，会触发重定向，返回状态码为307
            headers={
                "Authorization": f"Bearer {access_token}",
                "accept": "application/json",
            },
        )
        assert response.status_code == 200
        info = response.json()
        assert isinstance(info, list)
        if info:
            assert "username" in info[0]
            assert "email" in info[0]
            assert "is_active" in info[0]
            assert "role_id" in info[0]


@pytest.mark.asyncio
async def test_read_me():
    access_token = await fetch_access_token()
    async with AsyncClient(app=app, base_url=base_url) as client:
        response = await client.get(
            "/users/me",
            headers={
                "Authorization": f"Bearer {access_token}",
                "accept": "application/json",
            },
        )
        assert response.status_code == 200
        info = response.json()
        assert "username" in info
        assert "email" in info
        assert "is_active" in info
        assert "role_id" in info


@pytest.mark.asyncio
async def test_read_user_by_id():
    access_token = await fetch_access_token()
    async with AsyncClient(app=app, base_url=base_url) as client:
        response = await client.get(
            "/users/1",
            headers={
                "Authorization": f"Bearer {access_token}",
                "accept": "application/json",
            },
        )
        assert response.status_code == 200
        info = response.json()
        assert "username" in info
        assert "email" in info
        assert "is_active" in info
        assert "role_id" in info


@pytest.mark.asyncio
async def test_update_user():
    access_token = await fetch_access_token()
    async with AsyncClient(app=app, base_url=base_url) as client:
        response = await client.put(
            "/users/2",
            json={
                "username": "tempUser",
                "email": "user@gmail.com",
                "is_active": True,
                "role_id": 1,
            },
            headers={
                "Authorization": f"Bearer {access_token}",
                "accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        assert response.status_code == 200
        info = response.json()
        assert info["username"] == "tempUser"
        assert info["email"] == "user@gmail.com"
        assert info["is_active"]
        assert info["role_id"] == 1


@pytest.mark.asyncio
async def test_delete_user():
    access_token = await fetch_access_token()
    async with AsyncClient(app=app, base_url=base_url) as client:
        response = await client.delete(
            "/users/2",
            headers={
                "Authorization": f"Bearer {access_token}",
                "accept": "application/json",
            },
        )
        assert response.status_code == 200
        assert "message" in response.json()
