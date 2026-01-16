from fastapi import UploadFile
from app.schemas.receipt import ReceiptResult, ReceiptItem
from typing import Optional
import re


class AnalyzerService:
    async def analyze(
        self,
        file: Optional[UploadFile] = None,
        text: Optional[str] = None,
    ) -> ReceiptResult:
        if text:
            return self._analyze_text(text)

        if file:
            return await self._analyze_receipt(file)

        # This should never happen because router validates input
        raise ValueError("Invalid input")


    def _analyze_text(self, text: str) -> ReceiptResult:
        # Very naive amount extraction for now
        amount_match = re.search(r"(\d+[.,]?\d*)", text)
        amount = float(amount_match.group(1).replace(",", ".")) if amount_match else 0.0

        return ReceiptResult(
            type="text",
            merchant=None,
            total=amount,
            currency="THB",  # temporary default
            date=None,
            items=[],
            confidence=0.4,
            language="auto",
        )


    async def _analyze_receipt(self, file: UploadFile) -> ReceiptResult:
        # Placeholder implementation for receipt analysis
        return ReceiptResult(
            type="receipt",
            merchant="Unknown",
            total=0.0,
            currency="UNKNOWN",
            date=None,
            items=[],
            confidence=0.1,
            language="auto",
        )