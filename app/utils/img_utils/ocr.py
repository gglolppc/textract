from openai import OpenAI, OpenAIError
from app.schemas.ocr_response import OCRResponse
from app.config import settings

client = OpenAI(api_key=settings.openai_api_key)



def run_ocr(link: str, language: str = "original") -> tuple[OCRResponse, int]:
    try:
        prompt = (
            f"You are an OCR and translation system. Extract text from the image and translate it into {language}. "
            f"Always return a valid JSON with fields: "
            f'{{"extracted_text": "...", "translated_text": "...", "status": "...", '
            f'"fail_reason": "...", "fail_reason_code": "...", "confidence": "...", "notes": "..."}}. '
            f"Possible values for 'status': success, partial, fail. "
            f"If the image contains illegal, harmful, or sensitive content that cannot be processed, "
            f"set status='fail', extracted_text='', translated_text='', and provide fail_reason='Sensitive content, request banned' "
            f"and fail_reason_code='sensitive_content'. "
            f"Never refuse or explain outside of JSON, always fill the JSON strictly."
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
