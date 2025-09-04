from openai import OpenAI, OpenAIError

from app.config import settings

client = OpenAI(api_key=settings.openai_api_key)

def run_ocr(link: str, language: str = "original") -> str:
    try:
        if language == "original":
            prompt = (
                "You are an OCR system. Your only task is to extract text from the image "
                "and return it exactly as it appears. Do not analyze, interpret, comment, "
                "or filter anything. Always try to extract as much text as possible, even if "
                "the text is unclear, messy, or partially unreadable."
            )
        else:
            prompt = (
                f"You are an OCR and translation system. Extract all text from the image "
                f"and translate it into {language}. Return only the translated text. "
                "Do not analyze, interpret, comment, or filter anything. "
                "Always try to extract and translate as much text as possible, "
                "even if the text is unclear, messy, or partially unreadable."
            )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
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
        if isinstance(content, list):
            return "".join([c["text"] for c in content if c["type"] == "text"])
        return str(content)

    except OpenAIError:
        return "Upload error"


