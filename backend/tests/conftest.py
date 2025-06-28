"""
Test configuration and fixtures for the Enterprise Insights Copilot backend.
"""

import pytest
import asyncio
import os
import sys
from typing import AsyncGenerator
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.core.config import settings

# Test environment variables
os.environ["ENVIRONMENT"] = "test"
os.environ["LOG_LEVEL"] = "INFO"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client() -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI application."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_csv_content() -> str:
    """Sample CSV content for testing file uploads."""
    return """Name,Age,City,Salary
John Doe,30,New York,50000
Jane Smith,25,Los Angeles,55000
Bob Johnson,35,Chicago,60000
Alice Brown,28,Houston,52000
Charlie Wilson,32,Phoenix,58000"""


@pytest.fixture
def sample_json_data() -> dict:
    """Sample JSON data for testing."""
    return {
        "users": [
            {"id": 1, "name": "John Doe", "age": 30, "city": "New York"},
            {"id": 2, "name": "Jane Smith", "age": 25, "city": "Los Angeles"},
            {"id": 3, "name": "Bob Johnson", "age": 35, "city": "Chicago"}
        ],
        "metadata": {
            "total_count": 3,
            "created_at": "2025-06-28T10:00:00Z"
        }
    }


@pytest.fixture
def mock_session_id() -> str:
    """Mock session ID for testing."""
    return "test-session-123"


@pytest.fixture
def mock_execution_id() -> str:
    """Mock execution ID for testing."""
    return "test-execution-456"


@pytest.fixture
def mock_file_id() -> str:
    """Mock file ID for testing."""
    return "test-file-789"


class MockPineconeClient:
    """Mock Pinecone client for testing."""
    
    def __init__(self):
        self.vectors = {}
    
    def upsert(self, vectors):
        for vector in vectors:
            self.vectors[vector["id"]] = vector
    
    def query(self, vector, top_k=10, include_metadata=True):
        # Simple mock implementation
        matches = list(self.vectors.values())[:top_k]
        return {"matches": matches}
    
    def delete(self, ids):
        for id in ids:
            if id in self.vectors:
                del self.vectors[id]


@pytest.fixture
def mock_pinecone_client():
    """Mock Pinecone client fixture."""
    return MockPineconeClient()


@pytest.fixture
def mock_ollama_response():
    """Mock Ollama response for testing."""
    return {
        "model": "llama3.1:8b",
        "created_at": "2025-06-28T10:00:00.000Z",
        "response": "This is a mock response from the Llama model.",
        "done": True,
        "context": [1, 2, 3, 4, 5],
        "total_duration": 1000000000,
        "load_duration": 500000000,
        "prompt_eval_count": 10,
        "prompt_eval_duration": 200000000,
        "eval_count": 20,
        "eval_duration": 300000000
    }


# Test database configuration
@pytest.fixture
def test_db_settings():
    """Override database settings for testing."""
    original_db_url = settings.DATABASE_URL
    settings.DATABASE_URL = "sqlite:///./test.db"
    yield settings
    settings.DATABASE_URL = original_db_url


# Utility functions for tests
def create_mock_file(filename: str, content: str, content_type: str = "text/csv"):
    """Create a mock file for testing uploads."""
    from io import BytesIO
    file_obj = BytesIO(content.encode('utf-8'))
    file_obj.name = filename
    return file_obj


def assert_response_structure(response_data: dict, required_fields: list):
    """Assert that response contains required fields."""
    for field in required_fields:
        assert field in response_data, f"Missing field: {field}"


def assert_error_response(response_data: dict, expected_error: str = None):
    """Assert that response is an error with optional error message check."""
    assert "error" in response_data or "detail" in response_data
    if expected_error:
        error_msg = response_data.get("error", response_data.get("detail", ""))
        assert expected_error in str(error_msg)
