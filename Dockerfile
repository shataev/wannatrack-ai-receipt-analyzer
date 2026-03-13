# Use official Python slim image for smaller size
FROM python:3.12-slim

# Set working directory in the container
WORKDIR /app

# Install system dependencies required by pytesseract (OCR)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Expose the port uvicorn listens on
EXPOSE 8000

# Run the FastAPI app with uvicorn (bind to 0.0.0.0 for container access)
# Pass OPENAI_API_KEY via environment at runtime (e.g. docker run -e or docker-compose env_file)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
