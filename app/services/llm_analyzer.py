import json
import logging
from typing import Dict, Any
from app.core.openai_client import client
from app.services.prompts import RECEIPT_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)


class LLMAnalyzer:
    """Service for analyzing receipt text using OpenAI LLM with retry logic"""
    
    MAX_RETRIES = 2
    
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze receipt text using OpenAI LLM with retry logic.
        
        Args:
            text: Receipt text to analyze
            
        Returns:
            Dict with parsed JSON response from LLM
            
        Raises:
            ValueError: If LLM returns invalid JSON after all retries
            Exception: If OpenAI API call fails after all retries
        """
        last_error = None
        
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": RECEIPT_ANALYSIS_PROMPT},
                        {"role": "user", "content": text},
                    ],
                    temperature=0.2,
                )

                content = response.choices[0].message.content
                
                # Try to parse JSON response
                try:
                    parsed = json.loads(content)
                    if attempt > 0:
                        logger.info(f"LLM call succeeded on attempt {attempt + 1}")
                    return parsed
                except json.JSONDecodeError as e:
                    last_error = ValueError(
                        f"LLM returned invalid JSON on attempt {attempt + 1}: {str(e)}. "
                        f"Response content: {content[:200]}..."
                    )
                    logger.warning(
                        f"Invalid JSON from LLM (attempt {attempt + 1}/{self.MAX_RETRIES + 1}): {str(e)}"
                    )
                    if attempt < self.MAX_RETRIES:
                        continue
                    raise last_error
                    
            except Exception as e:
                last_error = e
                logger.warning(
                    f"OpenAI API call failed (attempt {attempt + 1}/{self.MAX_RETRIES + 1}): {str(e)}"
                )
                if attempt < self.MAX_RETRIES:
                    continue
                raise
        
        # Should not reach here, but just in case
        if last_error:
            raise last_error
        raise ValueError("LLM analysis failed for unknown reason")