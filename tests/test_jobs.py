from fastapi.testclient import TestClient
from main import app
import uuid

client = TestClient(app)


def create_test_user_login_and_company():
    email = f"jobuser_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123"

    client.post(
        "/api/v1/register",
        json={
            "full_name": "Job Test User",
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

    headers = {
        "X-Auth-Token": token
    }

    company_response = client.post(
        "/api/v1/companies",
        headers=headers,
        json={
            "name": "Amazon",
            "website_url": "https://www.amazon.com",
            "industry": "Technology"
        }
    )

    company_id = company_response.json()["id"]

    return headers, company_id


def test_create_job():
    headers, company_id = create_test_user_login_and_company()

    response = client.post(
        "/api/v1/jobs",
        headers=headers,
        json={
            "company_id": company_id,
            "job_title": "Python Developer",
            "status": "APPLIED",
            "work_model": "REMOTE",
            "location": "Berlin",
            "salary_min": 30000,
            "salary_max": 50000,
            "currency": "GBP",
            "job_description_url": "https://www.amazon.jobs"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["job_title"] == "Python Developer"
    assert data["company_id"] == company_id


def test_get_jobs():
    headers, company_id = create_test_user_login_and_company()

    client.post(
        "/api/v1/jobs",
        headers=headers,
        json={
            "company_id": company_id,
            "job_title": "Data Analyst",
            "status": "APPLIED",
            "work_model": "HYBRID",
            "location": "London",
            "salary_min": 30000,
            "salary_max": 45000,
            "currency": "GBP",
            "job_description_url": "https://www.amazon.jobs"
        }
    )

    response = client.get(
        "/api/v1/jobs",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1