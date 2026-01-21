from pydantic import BaseModel, field_validator
from typing import List, Optional, Literal
import re

class ReceiptItemLLM(BaseModel):
    name: str
    price: float

class ReceiptLLMResult(BaseModel):
    merchant: Optional[str]
    total: float
    currency: str  # ISO 4217 currency code (3 uppercase letters) or "UNKNOWN"
    date: Optional[str]
    items: List[ReceiptItemLLM]
    language: str  # ISO 639-1 language code (2 lowercase letters) or "auto"
    confidence: float
    
    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency is ISO 4217 format (3 uppercase letters) or UNKNOWN"""
        if v == "UNKNOWN":
            return v
        if not re.match(r'^[A-Z]{3}$', v):
            raise ValueError(f"Currency must be ISO 4217 format (3 uppercase letters) or 'UNKNOWN', got: {v}")
        return v
    
    @field_validator('language')
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Validate language is ISO 639-1 format (2 lowercase letters) or auto, normalize case"""
        v_lower = v.lower()
        if v_lower == "auto":
            return "auto"
        if not re.match(r'^[a-z]{2}$', v_lower):
            raise ValueError(f"Language must be ISO 639-1 format (2 lowercase letters) or 'auto', got: {v}")
        return v_lower