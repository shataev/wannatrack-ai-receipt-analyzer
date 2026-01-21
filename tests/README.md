# Tests Documentation

## Running Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_analyzer_service.py

# Run specific test
pytest tests/test_analyzer_service.py::TestAnalyzerService::test_analyze_text_success
```

## Test Structure

- `conftest.py` - Shared fixtures and pytest configuration
- `test_analyzer_service.py` - Tests for AnalyzerService
- `test_analyze_endpoint.py` - Tests for FastAPI `/analyze` endpoint

## Test Coverage

### AnalyzerService Tests
- ✅ `analyze_text()` - Validates correct ReceiptResult formation
- ✅ `analyze()` with text input
- ✅ `analyze()` with file input (OCR path)
- ✅ Error handling for no input
- ✅ Pydantic schema validation

### Endpoint Tests
- ✅ POST `/analyze` with text only
- ✅ POST `/analyze` with file only
- ✅ Error: no input (400)
- ✅ Error: both inputs (400)
- ✅ Response schema validation

