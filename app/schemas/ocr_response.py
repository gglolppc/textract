from pydantic import BaseModel, Field
from typing import Literal


class OCRResponse(BaseModel):
    extracted_text: str = Field(default="", description="Raw text extracted from the image")
    translated_text: str = Field(default="", description="Translated text (empty if language=original)")
    status: Literal["success", "partial", "fail"]
    fail_reason: str = Field(default="", description="Explanation if OCR/translation failed")
    fail_reason_code: str = Field(default="", description="Machine-readable code: no_text, unreadable, sensitive_content, bad_format...")
    confidence: Literal["high", "medium", "low", "none"] = "none"
    notes: str = Field(default="", description="Optional additional notes")
