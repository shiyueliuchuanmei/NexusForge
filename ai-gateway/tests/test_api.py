"""Unit tests for API routes."""
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine, SessionLocal


@pytest.fixture(scope="module")
def client():
    """Create test client."""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, client):
        """Test health endpoint returns healthy."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "endpoints" in data


class TestChatEndpoint:
    """Tests for chat completions endpoint."""

    def test_chat_without_api_key(self, client):
        """Test chat endpoint without API key returns 401."""
        response = client.post(
            "/v1/chat/completions",
            json={
                "model": "gpt-4",
                "messages": [{"role": "user", "content": "Hello"}]
            }
        )
        assert response.status_code == 401

    def test_chat_with_invalid_api_key(self, client):
        """Test chat endpoint with invalid API key returns 401."""
        response = client.post(
            "/v1/chat/completions",
            headers={"x-api-key": "invalid-key"},
            json={
                "model": "gpt-4",
                "messages": [{"role": "user", "content": "Hello"}]
            }
        )
        assert response.status_code == 401


class TestAdminEndpoint:
    """Tests for admin endpoints."""

    def test_admin_without_key(self, client):
        """Test admin endpoint without key returns 401."""
        response = client.get("/admin/users")
        assert response.status_code == 401

    def test_admin_with_invalid_key(self, client):
        """Test admin endpoint with invalid key returns 403."""
        response = client.get(
            "/admin/users",
            headers={"x-admin-key": "invalid-key"}
        )
        assert response.status_code == 403
