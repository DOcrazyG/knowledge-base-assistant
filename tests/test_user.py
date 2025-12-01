import pytest
from httpx import AsyncClient

from app.main import app


@pytest.fixture
def async_backend():
    return "asyncio"


@pytest.mark.asyncio
async def test_create_user():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.post(
            "/login/token",
            data={"username": "admin", "password": "123456"},
        )
        token_info = response.json()
        response = await client.post(
            "/users/register",
            json={
                "username": "test01",
                "email": "test01@gmail.com",
                "password": "test01",
                "is_active": True,
                "role_id": 1,
            },
            headers={"Authorization": f"Bearer {token_info['access_token']}"},
        )
        assert response.status_code == 200
        assert "is_active" in response.json()
        assert "role_id" in response.json()
