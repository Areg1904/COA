import pytest
import httpx
import os

import posts_pb2, posts_pb2_grpc

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

def test_post(client):
    login_data = {"email": "testuser@example.com", "password": "testpassword"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 200, f"Failed to login: {response.text}"
    token = response.json()["access_token"]

    post_data = {
        "title": "Test Post",
        "description": "This is a test post description.",
        "privacy_flag": False,
        "tags": ["test", "example"]
    }

    response = client.put("/create-post", json=post_data, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200, f"Failed to create post: {response.text}"
    assert "post_id" in response.json(), "Post ID not returned in response"
    post_id = response.json()['post_id']

    post_data_update = {
        "title": "Test Post (updated)",
        "description": "This is a test post description. (updated)",
        "privacy_flag": True,
        "tags": ["test", "example", "(updated)"]
    }

    response = client.put(f"/update-post/{post_id}", json=post_data_update, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200, f"Failed to update post: {response.text}"
    assert response.json()['message'] == "Post updated successfully", "Post ID not returned in response"

    response = client.get(f"/get-post/{post_id}", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200, f"Failed to get post: {response.text}"
    assert response.json()['title'] == post_data_update['title'], "Title does not match updated title"
    assert response.json()['description'] == post_data_update['description'], "Description does not match updated description"
    assert response.json()['privacy_flag'] == post_data_update['privacy_flag'], "Privacy flag does not match updated privacy flag"
    assert response.json()['tags'] == post_data_update['tags'], "Tags do not match updated tags"

    response = client.delete(f"/delete-post/{post_id}", headers={"Authorization": f"Bearer {token}"})

    assert response.json()['message'] == "Post deleted successfully"

def test_get_posts(client):
    login_data = {"email": "testuser@example.com", "password": "testpassword"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 200, f"Failed to login: {response.text}"
    token = response.json()["access_token"]

    post_data1 = {
        "title": "Test Post 1",
        "description": "This is a test post description. 1",
        "privacy_flag": False,
        "tags": ["test 1", "example 1"]
    }

    post_data2 = {
        "title": "Test Post 2",
        "description": "This is a test post description. 2",
        "privacy_flag": True,
        "tags": ["test 2", "example 2"]
    }

    post_data3 = {
        "title": "Test Post 3",
        "description": "This is a test post description. 3",
        "privacy_flag": False,
        "tags": ["test 3", "example 3"]
    }

    response = client.put("/create-post", json=post_data1, headers={"Authorization": f"Bearer {token}"})
    response = client.put("/create-post", json=post_data2, headers={"Authorization": f"Bearer {token}"})
    response = client.put("/create-post", json=post_data3, headers={"Authorization": f"Bearer {token}"})
    
    response = client.get("/get-posts?page_number=1&page_size=10", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200, f"Failed to get post: {response.text}"
    assert len(response.json()["posts"]) == 2
    for ind, post_data in enumerate([post_data1, post_data3]):
        assert response.json()["posts"][ind]['title'] == post_data['title'], "Title does not match updated title"
        assert response.json()["posts"][ind]['description'] == post_data['description'], "Description does not match updated description"
        assert response.json()["posts"][ind]['privacy_flag'] == post_data['privacy_flag'], "Privacy flag does not match updated privacy flag"
        assert response.json()["posts"][ind]['tags'] == post_data['tags'], "Tags do not match updated tags"