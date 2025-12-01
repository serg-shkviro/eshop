"""
Тесты эндпоинтов аутентификации
"""

import pytest
from fastapi import status


class TestAuthentication:
    
    def test_register_user_success(self, client):
        user_data = {
            "name": "New User",
            "email": "newuser@example.com",
            "password": "securepassword123",
            "phone": "+1234567890",
            "address": "123 New Street"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["name"] == user_data["name"]
        assert "id" in data
        assert "hashed_password" not in data
    
    def test_register_duplicate_email(self, client, test_user):
        user_data = {
            "name": "Another User",
            "email": test_user.email,
            "password": "password123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_invalid_email(self, client):
        user_data = {
            "name": "Test User",
            "email": "invalid-email",
            "password": "password123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_success(self, client, test_user, test_user_data):
        response = client.post(
            "/auth/login",
            data={
                "username": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, test_user):
        response = client.post(
            "/auth/login",
            data={
                "username": test_user.email,
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client):
        response = client.post(
            "/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user(self, client, test_user, auth_headers):
        response = client.get("/auth/me", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name
    
    def test_get_current_user_no_token(self, client):
        response = client.get("/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_invalid_token(self, client):
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUserProfile:
    
    def test_get_my_profile(self, client, test_user, auth_headers):
        response = client.get("/users/me", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["id"] == test_user.id
    
    def test_update_my_profile(self, client, auth_headers):
        update_data = {
            "name": "Updated Name",
            "phone": "+9876543210"
        }
        
        response = client.put("/users/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["phone"] == update_data["phone"]
    
    def test_update_profile_no_auth(self, client):
        update_data = {"name": "New Name"}
        response = client.put("/users/me", json=update_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

