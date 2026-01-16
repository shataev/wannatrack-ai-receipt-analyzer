from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from app.services.analyzer import AnalyzerService
from app.schemas.receipt import ReceiptResult

router = APIRouter()
analyzer = AnalyzerService()


@router.post("/analyze", response_model=ReceiptResult)
async def analyze(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
):
    # Validate input: exactly one source must be provided
    if not file and not text:
        raise HTTPException(status_code=400, detail="Either file or text must be provided")

    if file and text:
        raise HTTPException(status_code=400, detail="Provide only one input source")

     # Delegate processing to the service
    return await analyzer.analyze(file=file, text=text)