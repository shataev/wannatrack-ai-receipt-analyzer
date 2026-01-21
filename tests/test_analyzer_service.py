"""
Tests for AnalyzerService
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from app.services.analyzer import AnalyzerService
from app.schemas.receipt import ReceiptResult, ReceiptItem
from app.schemas.receipt_llm import ReceiptLLMResult


class TestAnalyzerService:
    """Test suite for AnalyzerService"""

    @pytest.fixture
    def analyzer(self):
        """Create AnalyzerService instance"""
        return AnalyzerService()

    @pytest.mark.asyncio
    async def test_analyze_text_success(self, analyzer, mock_llm_response):
        """Test analyze_text returns correct ReceiptResult structure"""
        # Mock LLM analyzer to return predefined response
        with patch.object(analyzer.llm, 'analyze_text', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_llm_response

            result = await analyzer.analyze_text("Test receipt text")

            # Verify LLM was called with correct text
            mock_llm.assert_called_once_with("Test receipt text")

            # Verify result is ReceiptResult instance
            assert isinstance(result, ReceiptResult)

            # Verify structure and values
            assert result.type == "text"
            assert result.merchant == "Test Store"
            assert result.total == 150.50
            assert result.currency == "USD"
            assert result.date == "2024-01-15"
            assert result.confidence == 0.95
            assert result.language == "en"

            # Verify items structure
            assert len(result.items) == 2
            assert isinstance(result.items[0], ReceiptItem)
            assert result.items[0].name == "Item 1"
            assert result.items[0].price == 50.00
            assert result.items[1].name == "Item 2"
            assert result.items[1].price == 100.50

    @pytest.mark.asyncio
    async def test_analyze_text_with_null_values(self, analyzer):
        """Test analyze_text handles null values correctly"""
        mock_response = {
            "merchant": None,
            "total": 100.0,
            "currency": "EUR",
            "date": None,
            "items": [{"name": "Single item", "price": 100.0}],
            "language": "ru",
            "confidence": 0.8
        }

        with patch.object(analyzer.llm, 'analyze_text', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_response

            result = await analyzer.analyze_text("Test text")

            assert result.merchant is None
            assert result.date is None
            assert result.total == 100.0
            assert len(result.items) == 1

    @pytest.mark.asyncio
    async def test_analyze_with_text_only(self, analyzer, mock_llm_response):
        """Test analyze method with text input"""
        with patch.object(analyzer.llm, 'analyze_text', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = mock_llm_response

            result = await analyzer.analyze(text="Test receipt text")

            # Verify LLM was called
            mock_llm.assert_called_once_with("Test receipt text")

            # Verify result structure
            assert isinstance(result, ReceiptResult)
            assert result.type == "text"

    @pytest.mark.asyncio
    async def test_analyze_with_file(self, analyzer, mock_llm_response, mock_upload_file, mock_ocr_text):
        """Test analyze method with file input (OCR path)"""
        import os
        from unittest.mock import mock_open

        with patch.object(analyzer.ocr, 'extract_text') as mock_ocr:
            mock_ocr.return_value = mock_ocr_text

            with patch.object(analyzer.llm, 'analyze_text', new_callable=AsyncMock) as mock_llm:
                mock_llm.return_value = mock_llm_response

                # Mock file write operation
                with patch('builtins.open', mock_open()) as mock_file:
                    result = await analyzer.analyze(file=mock_upload_file)

                    # Verify file was written
                    mock_file.assert_called_once()
                    
                    # Verify OCR was called with correct file path
                    mock_ocr.assert_called_once()
                    call_args = mock_ocr.call_args[0]
                    assert call_args[0] == f"/tmp/{mock_upload_file.filename}"

                    # Verify LLM was called with OCR text
                    mock_llm.assert_called_once_with(mock_ocr_text)

                    # Verify result structure
                    assert isinstance(result, ReceiptResult)
                    assert result.type == "text"

    @pytest.mark.asyncio
    async def test_analyze_no_input_error(self, analyzer):
        """Test analyze raises ValueError when no input provided"""
        with pytest.raises(ValueError, match="No input provided"):
            await analyzer.analyze()

    @pytest.mark.asyncio
    async def test_analyze_both_inputs_uses_file_ocr_text(self, analyzer, mock_llm_response, mock_upload_file, mock_ocr_text):
        """Test analyze when both file and text provided - file is processed first, OCR text is used"""
        # Mock OCR to avoid real file operations
        with patch.object(analyzer.ocr, 'extract_text') as mock_ocr:
            mock_ocr.return_value = mock_ocr_text
            
            with patch.object(analyzer.llm, 'analyze_text', new_callable=AsyncMock) as mock_llm:
                mock_llm.return_value = mock_llm_response

                # When both are provided, current implementation processes file first
                # OCR text overwrites the passed text parameter
                with patch('builtins.open', mock_open()) as mock_file:
                    result = await analyzer.analyze(text="Direct text", file=mock_upload_file)

                    # Verify file was written
                    mock_file.assert_called_once()
                    
                    # Verify OCR was called
                    mock_ocr.assert_called_once()
                    
                    # Verify LLM was called with OCR text, not the passed text
                    mock_llm.assert_called_once_with(mock_ocr_text)
                    
                    # Verify result
                    assert isinstance(result, ReceiptResult)

    @pytest.mark.asyncio
    async def test_analyze_text_validates_pydantic_schema(self, analyzer):
        """Test that analyze_text validates LLM response through Pydantic"""
        invalid_response = {
            "merchant": "Test",
            "total": "not a number",  # Invalid type
            "currency": "USD",
            "date": "2024-01-15",
            "items": [],
            "language": "en",
            "confidence": 0.9
        }

        with patch.object(analyzer.llm, 'analyze_text', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = invalid_response

            # Should raise ValidationError from Pydantic
            with pytest.raises(Exception):  # Pydantic ValidationError
                await analyzer.analyze_text("Test text")

