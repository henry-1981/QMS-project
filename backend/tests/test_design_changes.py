import pytest
from fastapi import status


def test_list_design_changes_empty(client, test_user_data):
    client.post("/api/v1/auth/register", json=test_user_data)
    login_resp = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/design-changes/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []
