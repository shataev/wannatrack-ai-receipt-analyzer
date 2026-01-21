"""
Tests for /analyze FastAPI endpoint
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient
from app.main import app
from app.schemas.receipt import ReceiptResult


class TestAnalyzeEndpoint:
    """Test suite for /analyze endpoint"""

    @pytest.mark.asyncio
    async def test_analyze_with_text_only(self, async_client, mock_llm_response):
        """Test endpoint with text input only"""
        with patch('app.routers.analyze.analyzer') as mock_analyzer:
            # Create mock ReceiptResult
            from app.schemas.receipt import ReceiptResult, ReceiptItem
            mock_result = ReceiptResult(
                type="text",
                merchant="Test Store",
                total=150.50,
                currency="USD",
                date="2024-01-15",
                items=[
                    ReceiptItem(name="Item 1", price=50.00),
                    ReceiptItem(name="Item 2", price=100.50)
                ],
                confidence=0.95,
                language="en"
            )

            mock_analyzer.analyze = AsyncMock(return_value=mock_result)

            # Make request with text
            response = await async_client.post(
                "/analyze",
                data={"text": "Test receipt text"}
            )

            # Verify response
            assert response.status_code == 200
            data = response.json()

            # Verify structure matches ReceiptResult schema
            assert data["type"] == "text"
            assert data["merchant"] == "Test Store"
            assert data["total"] == 150.50
            assert data["currency"] == "USD"
            assert data["date"] == "2024-01-15"
            assert data["confidence"] == 0.95
            assert data["language"] == "en"
            assert len(data["items"]) == 2
            assert data["items"][0]["name"] == "Item 1"
            assert data["items"][0]["price"] == 50.00

            # Verify service was called correctly
            mock_analyzer.analyze.assert_called_once()
            call_kwargs = mock_analyzer.analyze.call_args[1]
            assert call_kwargs["text"] == "Test receipt text"
            assert call_kwargs["file"] is None

    @pytest.mark.asyncio
    async def test_analyze_with_file_only(self, async_client, mock_llm_response):
        """Test endpoint with file input only"""
        with patch('app.routers.analyze.analyzer') as mock_analyzer:
            from app.schemas.receipt import ReceiptResult, ReceiptItem
            mock_result = ReceiptResult(
                type="text",
                merchant="Store from OCR",
                total=200.0,
                currency="EUR",
                date=None,
                items=[ReceiptItem(name="OCR Item", price=200.0)],
                confidence=0.85,
                language="ru"
            )

            mock_analyzer.analyze = AsyncMock(return_value=mock_result)

            # Create fake file content
            files = {"file": ("receipt.jpg", b"fake image data", "image/jpeg")}

            # Make request with file
            response = await async_client.post(
                "/analyze",
                files=files
            )

            # Verify response
            assert response.status_code == 200
            data = response.json()

            # Verify structure
            assert data["type"] == "text"
            assert data["merchant"] == "Store from OCR"
            assert data["total"] == 200.0
            assert data["currency"] == "EUR"
            assert data["date"] is None
            assert len(data["items"]) == 1

            # Verify service was called with file
            mock_analyzer.analyze.assert_called_once()
            call_kwargs = mock_analyzer.analyze.call_args[1]
            assert call_kwargs["text"] is None
            assert call_kwargs["file"] is not None

    @pytest.mark.asyncio
    async def test_analyze_no_input_returns_400(self, async_client):
        """Test endpoint returns 400 when no input provided"""
        response = await async_client.post("/analyze")

        assert response.status_code == 400
        assert "Either file or text must be provided" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_analyze_both_inputs_returns_400(self, async_client):
        """Test endpoint returns 400 when both file and text provided"""
        files = {"file": ("receipt.jpg", b"fake image data", "image/jpeg")}
        data = {"text": "Test text"}

        response = await async_client.post(
            "/analyze",
            files=files,
            data=data
        )

        assert response.status_code == 400
        assert "Provide only one input source" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_analyze_response_validates_against_schema(self, async_client, mock_llm_response):
        """Test that endpoint response matches ReceiptResult Pydantic schema"""
        with patch('app.routers.analyze.analyzer') as mock_analyzer:
            from app.schemas.receipt import ReceiptResult, ReceiptItem
            mock_result = ReceiptResult(
                type="text",
                merchant="Schema Test",
                total=99.99,
                currency="THB",
                date="2024-12-31",
                items=[
                    ReceiptItem(name="Test Item", price=99.99)
                ],
                confidence=0.99,
                language="th"
            )

            mock_analyzer.analyze = AsyncMock(return_value=mock_result)

            response = await async_client.post(
                "/analyze",
                data={"text": "test"}
            )

            assert response.status_code == 200
            data = response.json()

            # Validate response can be parsed as ReceiptResult
            result = ReceiptResult(**data)
            assert isinstance(result, ReceiptResult)
            assert result.type == "text"
            assert result.merchant == "Schema Test"
            assert result.total == 99.99
            assert result.currency == "THB"
            assert result.language == "th"

    @pytest.mark.asyncio
    async def test_analyze_empty_text_returns_400(self, async_client):
        """Test endpoint returns 400 when text is empty string"""
        response = await async_client.post(
            "/analyze",
            data={"text": ""}
        )

        # Empty string is falsy, so should be treated as no input
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_analyze_with_null_values_in_response(self, async_client):
        """Test endpoint handles null values correctly in response"""
        with patch('app.routers.analyze.analyzer') as mock_analyzer:
            from app.schemas.receipt import ReceiptResult, ReceiptItem
            mock_result = ReceiptResult(
                type="text",
                merchant=None,
                total=50.0,
                currency="RUB",
                date=None,
                items=[ReceiptItem(name="Item", price=50.0)],
                confidence=0.7,
                language="auto"
            )

            mock_analyzer.analyze = AsyncMock(return_value=mock_result)

            response = await async_client.post(
                "/analyze",
                data={"text": "test"}
            )

            assert response.status_code == 200
            data = response.json()

            # Verify null values are included in JSON
            assert data["merchant"] is None
            assert data["date"] is None
            assert data["total"] == 50.0

