import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.main import app


class TestAPI:
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    async def async_client(self):
        """Create async test client."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

    def test_readiness_endpoint(self, client):
        """Test readiness check endpoint."""
        response = client.get("/readiness")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"

    @pytest.mark.asyncio
    async def test_async_health_endpoint(self, async_client):
        """Test health endpoint with async client."""
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.options("/health")
        assert response.status_code == 200
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers

    def test_request_id_middleware(self, client):
        """Test that request ID is added to responses."""
        response = client.get("/health")
        assert "x-request-id" in response.headers
        assert len(response.headers["x-request-id"]) > 0
