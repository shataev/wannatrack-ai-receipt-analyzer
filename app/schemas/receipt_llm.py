from pydantic import BaseModel
from typing import List, Optional, Literal

class ReceiptItemLLM(BaseModel):
    name: str
    price: float

class ReceiptLLMResult(BaseModel):
    merchant: Optional[str]
    total: float
    currency: Literal["USD", "EUR", "THB", "RUB", "UNKNOWN"]
    date: Optional[str]
    items: List[ReceiptItemLLM]
    language: Literal["en", "ru", "th", "auto"]
    confidence: float