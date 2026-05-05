# Wannatrack AI Analyzer

FastAPI microservice for AI-powered receipt analysis. Part of the [Wanna Track](https://github.com/shataev/wanna-track) expense tracking system.

Accepts a receipt image or plain text, runs OCR if needed, then uses an LLM to extract structured expense data.

## Part of the Wanna Track system

| Service | Stack | Description |
|---------|-------|-------------|
| [wanna-track](https://github.com/shataev/wanna-track) | Vue 3, Vite, Vuetify 3 | Web app for expense management |
| [wannatrack-receipt-api](https://github.com/shataev/wannatrack-receipt-api) | NestJS, TypeScript, Telegraf | Telegram bot + REST API |
| **wannatrack-ai-analyzer** | FastAPI, Python | This repo — OCR + LLM receipt parsing |

## Tech stack

- **FastAPI** — REST API
- **OCR** — image text extraction
- **LLM (OpenAI)** — structured data extraction from receipt text
- **Pydantic** — data validation

## API

### `POST /analyze`

Accepts a receipt image or plain text, returns structured expense data.

**Request** (multipart/form-data):
- `file` — receipt image (optional)
- `text` — receipt text (optional)

One of the two must be provided.

**Response:**
```json
{
  "merchant": "Tops Supermarket",
  "total": 350.0,
  "currency": "THB",
  "date": "2025-05-01",
  "items": [
    { "name": "Milk", "price": 45.0 },
    { "name": "Bread", "price": 35.0 }
  ],
  "confidence": 0.95,
  "language": "en"
}
```

The `confidence` field reflects how reliably the data was extracted. Values below 0.5 indicate uncertain results.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `.env`:

```env
OPENAI_API_KEY=your_openai_key
```

```bash
uvicorn app.main:app --reload
```

API available at `http://localhost:8000`
Interactive docs at `http://localhost:8000/docs`

## Project structure

```
app/
├── main.py           # FastAPI entry point
├── routers/
│   └── analyze.py    # POST /analyze endpoint
├── services/
│   ├── analyzer.py   # Orchestration: validate → OCR → LLM → normalize
│   ├── ocr_service.py
│   └── llm_analyzer.py
└── schemas/
    └── receipt.py    # Pydantic models
```
