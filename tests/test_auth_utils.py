"""
Тесты вспомогательных функций аутентификации
"""

import pytest
from app.auth import (
    verify_password, get_password_hash, create_access_token,
    authenticate_user
)


class TestPasswordHashing:
    
    def test_get_password_hash(self):
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_verify_password_success(self):
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_failure(self):
        password = "testpassword123"
        hashed = get_password_hash(password)
        wrong_password = "wrongpassword"
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_verify_password_with_bytes(self):
        password = "testpassword123"
        hashed = get_password_hash(password)
        hashed_bytes = hashed.encode('utf-8')
        
        assert verify_password(password, hashed_bytes) is True
    
    def test_verify_password_invalid_hash(self):
        password = "testpassword123"
        invalid_hash = "invalid_hash_string"
        
        assert verify_password(password, invalid_hash) is False


class TestTokenCreation:
    
    def test_create_access_token_with_expires_delta(self):
        from datetime import timedelta
        
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta=expires_delta)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_without_expires_delta(self):
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0


class TestAuthenticationUtils:
    
    def test_authenticate_user_success(self, db, test_user, test_user_data):
        user = authenticate_user(db, test_user_data["email"], test_user_data["password"])
        
        assert user is not None
        assert user.email == test_user_data["email"]
    
    def test_authenticate_user_wrong_password(self, db, test_user):
        user = authenticate_user(db, test_user.email, "wrongpassword")
        
        assert user is None
    
    def test_authenticate_user_nonexistent(self, db):
        user = authenticate_user(db, "nonexistent@example.com", "password123")
        
        assert user is None


class TestGetCurrentUser:
    
    def test_get_current_user_missing_email(self, client, db):
        from jose import jwt
        from app.config import settings
        from datetime import datetime, timedelta
        
        token_data = {"exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp())}
        token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
    
    def test_get_current_user_nonexistent_user(self, client, db):
        from jose import jwt
        from app.config import settings
        from datetime import datetime, timedelta
        
        token_data = {
            "sub": "nonexistent@example.com",
            "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp())
        }
        token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
    
    def test_get_current_user_inactive(self, client, db, test_user):
        from jose import jwt
        from app.config import settings
        from datetime import datetime, timedelta
        
        # Make user inactive
        test_user.is_active = 0
        db.commit()
        
        token_data = {
            "sub": test_user.email,
            "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp())
        }
        token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 400
        assert "inactive" in response.json()["detail"].lower()
    
    def test_get_current_active_user_inactive(self, client, db, test_user):
        from jose import jwt
        from app.config import settings
        from datetime import datetime, timedelta
        
        # Make user inactive
        test_user.is_active = 0
        db.commit()
        
        token_data = {
            "sub": test_user.email,
            "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp())
        }
        token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users/me", headers=headers)
        
        assert response.status_code == 400
        assert "inactive" in response.json()["detail"].lower()

