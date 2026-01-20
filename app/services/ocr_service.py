# app/services/ocr_service.py
from PIL import Image
import pytesseract

class OCRService:
    def __init__(self, lang='rus+eng'):
        self.lang = lang

    def extract_text(self, file_path: str) -> str:
        """Extract text from an image file"""
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image, lang=self.lang)
        return text.strip()