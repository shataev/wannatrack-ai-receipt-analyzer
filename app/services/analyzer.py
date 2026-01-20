from app.services.llm_analyzer import LLMAnalyzer
from app.schemas.receipt_llm import ReceiptLLMResult
from app.schemas.receipt import ReceiptResult, ReceiptItem
from app.services.ocr_service import OCRService

class AnalyzerService:
    def __init__(self):
        self.llm = LLMAnalyzer()
        self.ocr = OCRService()
        
    async def analyze(self, text: str = None, file=None):
        if file:
            # Save uploaded file temporarily
            file_path = f"/tmp/{file.filename}"
            with open(file_path, "wb") as f:
                f.write(await file.read())

            # Extract text via OCR
            text = self.ocr.extract_text(file_path)

        # For now we support text only.
        # File support (OCR) will be added later.
        if text:
            return await self.analyze_text(text)

        raise ValueError("No input provided")

    async def analyze_text(self, text: str) -> ReceiptLLMResult:
        # Call LLM service and get raw JSON-like response
        raw_result = await self.llm.analyze_text(text)

        # Validate and normalize response via Pydantic schema
        llm_result = ReceiptLLMResult(**raw_result)

        return ReceiptResult(
            type="text",
            merchant=llm_result.merchant,
            total=llm_result.total,
            currency=llm_result.currency,
            date=llm_result.date,
            items=[
                ReceiptItem(
                    name=item.name,
                    price=item.price,
                )
                for item in llm_result.items
            ],
            confidence=llm_result.confidence,
            language=llm_result.language,
        )