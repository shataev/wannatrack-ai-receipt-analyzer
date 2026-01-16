import re
from app.schemas.receipt import ReceiptResult, ReceiptItem


CURRENCY_MAP = {
    # Thai Baht
    "baht": "THB",
    "THB": "THB",
    "฿": "THB",
    "thb": "THB",
    
    # US Dollar
    "$": "USD",
    "usd": "USD",
    "dollar": "USD",

    # Euro
    "€": "EUR",
    "eur": "EUR",
    "euro": "EUR",

    # Russian Ruble
    "₽": "RUB",
    "rub": "RUB",
    "ruble": "RUB",
    "руб": "RUB",
    "рублей": "RUB",
    "рубля": "RUB",
    "рубль": "RUB",
}


class AnalyzerService:
    async def analyze(self, file=None, text=None):
        if text:
            return self._analyze_text(text)

        if file:
            return await self._analyze_receipt(file)

        raise ValueError("Invalid input")


    def _analyze_text(self, text: str) -> ReceiptResult:
        confidence = 0.0

        # Extract amount
        amount_match = re.search(r"(\d+[.,]?\d*)", text)
        total = float(amount_match.group(1).replace(",", ".")) if amount_match else 0.0
        if total:
            confidence += 0.4

        # Detect currency
        currency = "UNKNOWN"
        for key, value in CURRENCY_MAP.items():
            if key.lower() in text.lower():
                currency = value
                confidence += 0.2
                break

        # Detect merchant
        merchant_match = re.search(r"(?:at|в)\s+([A-Za-zА-Яа-я0-9\s]+)", text, re.IGNORECASE)
        merchant = merchant_match.group(1).strip() if merchant_match else None
        if merchant:
            confidence += 0.2

        # Detect language
        language = "ru" if re.search(r"[а-яА-Я]", text) else "en"
        confidence += 0.2

        return ReceiptResult(
            type="text",
            merchant=merchant,
            total=total,
            currency=currency,
            date=None,
            items=[],
            confidence=round(min(confidence, 1.0), 2),
            language=language,
        )

    async def _analyze_receipt(self, file: str) -> ReceiptResult:
    # Stub implementation for text analysis
        return ReceiptResult(
            type="file",
            merchant=None,
            total=0.0,
            currency="THB",
            date=None,
            items=[],
            confidence=0.2,
            language="auto",
        )