"""
Pytest configuration and shared fixtures
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def mock_llm_response():
    """Mock LLM response data"""
    return {
        "merchant": "Test Store",
        "total": 150.50,
        "currency": "USD",
        "date": "2024-01-15",
        "items": [
            {"name": "Item 1", "price": 50.00},
            {"name": "Item 2", "price": 100.50}
        ],
        "language": "en",
        "confidence": 0.95
    }


@pytest.fixture
def mock_ocr_text():
    """Mock OCR extracted text"""
    return "Test receipt text from OCR"


@pytest.fixture
def mock_upload_file():
    """Mock FastAPI UploadFile"""
    file = MagicMock()
    file.filename = "test_receipt.jpg"
    file.read = AsyncMock(return_value=b"fake image data")
    return file


@pytest.fixture
def client():
    """Synchronous test client for FastAPI"""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Asynchronous test client for FastAPI"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

