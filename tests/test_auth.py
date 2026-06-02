from fastapi.testclient import TestClient
from main import app
import uuid

client = TestClient(app)


def test_register_user():
    unique_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"

    response = client.post(
        "/api/v1/register",
        json={
            "full_name": "Test User",
            "email": unique_email,
            "password": "Password123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "User registered successfully"
    assert data["email"] == unique_email


def test_login_user():
    unique_email = f"testlogin_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123"

    client.post(
        "/api/v1/register",
        json={
            "full_name": "Login User",
            "email": unique_email,
            "password": password
        }
    )

    response = client.post(
        "/api/v1/login",
        json={
            "email": unique_email,
            "password": password
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["email"] == unique_email