"""
Тесты основных эндпоинтов приложения
"""

import pytest
from fastapi import status


class TestRootEndpoints:
    
    def test_read_root(self, client):
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert "version" in data
        assert data["version"] == "3.0.0"
        assert "docs" in data
        assert "authentication" in data
    
    def test_health_check(self, client):
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
