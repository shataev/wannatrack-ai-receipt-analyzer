import json
from app.core.openai_client import client
from app.schemas.receipt import ReceiptResult
from app.services.prompts import TEXT_ANALYSIS_PROMPT

class LLMAnalyzer:
    async def analyze_text(self, text: str) -> ReceiptResult:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": TEXT_ANALYSIS_PROMPT},
                {"role": "user", "content": text},
            ],
            temperature=0.2,
        )

        content = response.choices[0].message.content

        data = json.loads(content)

        return ReceiptResult(**data)