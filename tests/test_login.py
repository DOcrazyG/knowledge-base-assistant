import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

client = TestClient(app)


def test_login_success():
    response = client.post(
        "/login/token",
        data={"username": "admin", "password": "123456"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_failure():
    response = client.post(
        "/login/token",
        data={"username": "admin", "password": "wrong_password"},
    )
    assert response.status_code == 401
    assert "detail" in response.json()
    

def test_login_missing_credentials():
    response = client.post(
        "/login/token",
        data={"username": "admin"},
    )
    assert response.status_code == 422
    
    response = client.post(
        "/login/token",
        data={"password": "123456"},
    )
    assert response.status_code == 422