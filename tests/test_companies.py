from fastapi.testclient import TestClient
from main import app
import uuid

client = TestClient(app)


def create_test_user_and_login():
    email = f"companyuser_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123"

    client.post(
        "/api/v1/register",
        json={
            "full_name": "Company Test User",
            "email": email,
            "password": password
        }
    )

    login_response = client.post(
        "/api/v1/login",
        json={
            "email": email,
            "password": password
        }
    )

    token = login_response.json()["access_token"]

    return {
        "X-Auth-Token": token
    }


def test_create_company():
    headers = create_test_user_and_login()

    response = client.post(
        "/api/v1/companies",
        headers=headers,
        json={
            "name": "Google",
            "website_url": "https://www.google.com",
            "industry": "Technology"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Google"
    assert data["industry"] == "Technology"


def test_get_companies():
    headers = create_test_user_and_login()

    client.post(
        "/api/v1/companies",
        headers=headers,
        json={
            "name": "Microsoft",
            "website_url": "https://www.microsoft.com",
            "industry": "Technology"
        }
    )

    response = client.get(
        "/api/v1/companies",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1