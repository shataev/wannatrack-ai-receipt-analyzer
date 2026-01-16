from pydantic import BaseModel
from typing import List, Optional


class ReceiptItem(BaseModel):
    name: str
    price: float


class ReceiptResult(BaseModel):
    type: str  # "receipt" | "text"
    merchant: Optional[str]
    total: float
    currency: str
    date: Optional[str]
    items: List[ReceiptItem]
    confidence: float
    language: str