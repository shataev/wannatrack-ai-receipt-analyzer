import logging
from typing import Literal, Optional
from fastapi import UploadFile

from app.services.llm_analyzer import LLMAnalyzer
from app.schemas.receipt_llm import ReceiptLLMResult
from app.schemas.receipt import ReceiptResult, ReceiptItem
from app.services.ocr_service import OCRService

logger = logging.getLogger(__name__)

# Minimum text length for analysis
MIN_TEXT_LENGTH = 5


class AnalyzerService:
    """
    Main service for analyzing receipts from text or OCR.
    Orchestrates validation, LLM calls, and result normalization.
    """
    
    def __init__(self):
        self.llm = LLMAnalyzer()
        self.ocr = OCRService()
    
    async def analyze(self, text: Optional[str] = None, file: Optional[UploadFile] = None) -> ReceiptResult:
        """
        Main entry point for receipt analysis.
        Supports both direct text input and file upload (OCR).
        
        Args:
            text: Direct text input
            file: Uploaded file for OCR processing
            
        Returns:
            ReceiptResult with analyzed receipt data
            
        Raises:
            ValueError: If no input provided or input validation fails
        """
        source: Literal["text", "ocr"]
        processed_text: str
        
        if file:
            # Process file via OCR
            file_path = f"/tmp/{file.filename}"
            with open(file_path, "wb") as f:
                f.write(await file.read())
            
            processed_text = self.ocr.extract_text(file_path)
            source = "ocr"
        elif text:
            processed_text = text
            source = "text"
        else:
            raise ValueError("No input provided")
        
        # Analyze with validated input
        return await self._analyze_receipt(processed_text, source)
    
    async def _analyze_receipt(self, text: str, source: Literal["text", "ocr"]) -> ReceiptResult:
        """
        Internal method to analyze receipt text with source tracking.
        
        Args:
            text: Receipt text to analyze
            source: Source of the text ("text" or "ocr")
            
        Returns:
            ReceiptResult with analyzed data
        """
        # Validate input
        self._validate_input(text)
        
        # Log analysis start
        logger.info(
            f"Starting receipt analysis: source={source}, text_length={len(text)}"
        )
        
        try:
            # Call LLM for analysis
            raw_result = await self._call_llm(text)
            
            # Validate and normalize result
            result = self._validate_result(raw_result, source)
            
            logger.info(
                f"Receipt analysis completed: source={source}, "
                f"confidence={result.confidence}, total={result.total}"
            )
            
            return result
            
        except ValueError as e:
            # Re-raise validation errors (critical issues like invalid types)
            logger.error(
                f"Receipt analysis validation error: source={source}, error={str(e)}"
            )
            raise
        except Exception as e:
            # For other errors (LLM failures, network issues), return fallback
            logger.error(
                f"Receipt analysis failed: source={source}, error={str(e)}"
            )
            # Return low-confidence result for non-critical errors
            return self._create_fallback_result(source)
    
    def _validate_input(self, text: str) -> None:
        """
        Validate input text before processing.
        
        Args:
            text: Text to validate
            
        Raises:
            ValueError: If text is empty, too short, or contains only whitespace
        """
        if not text:
            raise ValueError("Text cannot be empty")
        
        # Strip whitespace and check length
        stripped = text.strip()
        if len(stripped) < MIN_TEXT_LENGTH:
            raise ValueError(
                f"Text is too short (minimum {MIN_TEXT_LENGTH} characters). "
                f"Got {len(stripped)} characters."
            )
    
    async def _call_llm(self, text: str) -> dict:
        """
        Call LLM analyzer and return raw result.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with raw LLM response
            
        Raises:
            Exception: If LLM call fails after retries
        """
        return await self.llm.analyze_text(text)
    
    def _validate_result(self, raw_result: dict, source: Literal["text", "ocr"]) -> ReceiptResult:
        """
        Validate LLM result and convert to ReceiptResult.
        Applies business rules and normalizes output.
        
        Args:
            raw_result: Raw dict from LLM
            source: Source of the text
            
        Returns:
            ReceiptResult with validated and normalized data
            
        Raises:
            ValueError: If Pydantic validation fails (invalid types/structure)
        """
        # Parse through Pydantic schema for type validation
        # Critical validation errors (invalid types) should raise exception
        try:
            llm_result = ReceiptLLMResult(**raw_result)
        except Exception as e:
            logger.error(f"LLM result validation failed (critical error): {str(e)}")
            # Re-raise for critical validation errors (invalid types)
            raise ValueError(f"Invalid LLM response structure: {str(e)}") from e
        
        # Apply business rules validation
        confidence = llm_result.confidence
        total = llm_result.total
        currency = llm_result.currency
        
        # Validate critical fields
        if total <= 0:
            logger.warning(f"Invalid total amount: {total}. Setting confidence to low.")
            confidence = min(confidence, 0.3)
        
        if not currency or currency == "UNKNOWN":
            logger.warning(f"Invalid or missing currency: {currency}. Setting confidence to low.")
            confidence = min(confidence, 0.3)
        
        # If data quality is poor, reduce confidence
        if confidence < 0.5:
            logger.info(f"Low confidence result detected: {confidence}")
        
        # Normalize output
        return self._normalize_output(llm_result, source, confidence)
    
    def _normalize_output(
        self, 
        llm_result: ReceiptLLMResult, 
        source: Literal["text", "ocr"],
        confidence: float
    ) -> ReceiptResult:
        """
        Convert LLM result to final ReceiptResult schema.
        
        Args:
            llm_result: Validated LLM result
            source: Source of the text
            confidence: Adjusted confidence value
            
        Returns:
            ReceiptResult ready for API response
        """
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
            confidence=confidence,
            language=llm_result.language,
        )
    
    def _create_fallback_result(self, source: Literal["text", "ocr"]) -> ReceiptResult:
        """
        Create fallback result when analysis fails.
        Returns low-confidence result instead of raising exception.
        
        Args:
            source: Source of the text
            
        Returns:
            ReceiptResult with minimal data and low confidence
        """
        return ReceiptResult(
            type="text",
            merchant=None,
            total=0.0,
            currency="UNKNOWN",
            date=None,
            items=[],
            confidence=0.1,
            language="auto",
        )
    
    async def analyze_text(self, text: str) -> ReceiptResult:
        """
        Legacy method for backward compatibility.
        Analyzes text input directly.
        
        Args:
            text: Text to analyze
            
        Returns:
            ReceiptResult with analyzed data
        """
        return await self._analyze_receipt(text, "text")
