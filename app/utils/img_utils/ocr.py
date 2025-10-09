from openai import OpenAI, OpenAIError
from app.schemas.ocr_response import OCRResponse
from app.config.config import settings

client = OpenAI(api_key=settings.openai_api_key)



def run_ocr(link: str, language: str = "original") -> tuple[OCRResponse, int]:
    try:
        prompt = (
            f"""
        You are an OCR and translation system.

        1. Extract all readable text from the image as accurately as possible.
        2. If the requested language is not "original", translate the extracted text **into that target language**.
        3. If the requested language *is* "original", do not translate — just return the original text.

        Return **strictly valid JSON** with the following fields:
        {{
          "extracted_text": "...",
          "translated_text": "...",
          "status": "success | partial | fail",
          "fail_reason": "...",
          "fail_reason_code": "...",
          "confidence": "high | medium | low",
          "notes": "..."
        }}

        Additional rules:
        - Always include *both* "extracted_text" and "translated_text" fields — even if they are identical.
        - Never output text outside JSON.
        - If you detect illegal, harmful, or sensitive content, set:
          status = "fail",
          extracted_text = "",
          translated_text = "",
          fail_reason = "Sensitive content, request banned",
          fail_reason_code = "sensitive_content".
        - If translation is impossible, leave "translated_text" empty and set status="partial".

        Requested target language: "{language}".
        """
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},  # 👈 гарантия JSON
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": link}},
                    ],
                }
            ],
        )

        content = response.choices[0].message.content
        print(content)

        tokens = response.usage.total_tokens if response.usage else 0

        try:
            return OCRResponse.model_validate_json(content), tokens
        except Exception:
            return OCRResponse(
                extracted_text="",
                translated_text="",
                status="fail",
                fail_reason="Invalid JSON format from model",
                fail_reason_code="bad_format",
                confidence="none",
                notes="",
            ), tokens

    except OpenAIError as e:
        return OCRResponse(
            extracted_text="",
            translated_text="",
            status="fail",
            fail_reason=f"OpenAI API error: {str(e)}",
            fail_reason_code="openai_error",
            confidence="none",
            notes="",
        ), 0
