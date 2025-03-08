import pytest
import httpx
import os

API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://api-gateway:8000")

@pytest.fixture(scope="module")
def client():
    with httpx.Client(base_url=API_GATEWAY_URL) as client:
        yield client

def test_register(client):
    user_data = {
        "email": "testuser@example.com",
        "password": "testpassword",
        "user_info": {
            "first_name": "Test",
            "last_name": "User",
            "birth_date": "2000-01-01",
            "phone": "+1234567890"
        }
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 200, f"Failed to register user: {response.text}"
    assert response.json() == {"message": "User registered successfully"}

def test_login(client):
    login_data = {"email": "testuser@example.com", "password": "testpassword"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 200, f"Failed to login: {response.text}"
    assert response.json()["message"] == "Login successful"

def test_get_profile(client):
    login_data = {"email": "testuser@example.com", "password": "testpassword"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 200, f"Failed to login: {response.text}"
    token = response.json()["access_token"]

    response = client.get("/profile", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    profile = response.json()
    assert profile["email"] == "testuser@example.com"
    assert profile["first_name"] == "Test"
    assert profile["last_name"] == "User"
    assert profile["birth_date"] == "2000-01-01"
    assert profile["phone"] == "+1234567890"

def test_update_profile(client):
    login_data = {"email": "testuser@example.com", "password": "testpassword"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 200, f"Failed to login: {response.text}"
    token = response.json()["access_token"]

    updated_info = {
        "first_name": "Updated",
        "last_name": "User",
        "birth_date": "2000-02-02",
        "phone": "+1987654321"
    }
    response = client.put("/update-profile", json=updated_info, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"message": "Profile updated successfully"}

    response = client.get("/profile", headers={"Authorization": f"Bearer {token}"})
    profile = response.json()
    assert profile["first_name"] == "Updated"
    assert profile["last_name"] == "User"
    assert profile["birth_date"] == "2000-02-02"
    assert profile["phone"] == "+1987654321"
