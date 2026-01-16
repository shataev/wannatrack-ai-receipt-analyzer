# Wannatrack AI Receipt Analyzer

A FastAPI-based service for analyzing receipts and extracting structured data from text or image files.

## Features

- **Receipt Analysis**: Extract structured data from receipt images
- **Text Analysis**: Parse receipt information from plain text
- **RESTful API**: Simple HTTP endpoints for integration
- **Structured Output**: Returns standardized receipt data with items, totals, and metadata

## Project Structure

```
wannatrack-ai-analyzer/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── routers/
│   │   └── analyze.py       # API routes for receipt analysis
│   ├── services/
│   │   └── analyzer.py      # Business logic for receipt analysis
│   └── schemas/
│       └── receipt.py       # Pydantic models for data validation
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd wannatrack-ai-analyzer
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Start the FastAPI server using uvicorn:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

- API Documentation: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## API Endpoints

### POST `/analyze`

Analyzes a receipt from either a file upload or text input.

**Request:**
- **file** (optional): Receipt image file (multipart/form-data)
- **text** (optional): Plain text containing receipt information

**Note:** Exactly one of `file` or `text` must be provided.

**Response:**
```json
{
  "type": "receipt" | "text",
  "merchant": "string | null",
  "total": 0.0,
  "currency": "string",
  "date": "string | null",
  "items": [
    {
      "name": "string",
      "price": 0.0
    }
  ],
  "confidence": 0.0,
  "language": "string"
}
```

**Example with curl:**

Using text input:
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "text=Total: 150.50 THB"
```

Using file upload:
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@receipt.jpg"
```

## Development

The project uses:
- **FastAPI**: Modern web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server for running the application

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

