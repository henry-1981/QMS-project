import pytest
from fastapi import status


def test_register_user(client, test_user_data):
    response = client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == test_user_data["username"]
    assert data["email"] == test_user_data["email"]
    assert "id" in data


def test_register_duplicate_username(client, test_user_data):
    client.post("/api/v1/auth/register", json=test_user_data)
    response = client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"]


def test_login_success(client, test_user_data):
    client.post("/api/v1/auth/register", json=test_user_data)
    
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    response = client.post(
        "/api/v1/auth/login",
        data=login_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user_data):
    client.post("/api/v1/auth/register", json=test_user_data)
    
    login_data = {
        "username": test_user_data["username"],
        "password": "wrongpassword"
    }
    response = client.post(
        "/api/v1/auth/login",
        data=login_data
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_nonexistent_user(client):
    login_data = {
        "username": "nonexistent",
        "password": "password"
    }
    response = client.post(
        "/api/v1/auth/login",
        data=login_data
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
