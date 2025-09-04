import base64
from pathlib import Path
from openai import OpenAI, OpenAIError

from app.config import settings

client = OpenAI(api_key=settings.openai_api_key)

def run_ocr(link: str, language: str = "original") -> str:
    try:
        if language == "original":
            prompt = "Extract all text from this image as it is."
        else:
            prompt = f"Extract text from this image and translate it into {language}. Return only the translated text."

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


