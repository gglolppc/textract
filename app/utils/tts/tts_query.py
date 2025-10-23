from openai import OpenAI
import tempfile
from app.config.config import settings
import tiktoken

client = OpenAI(api_key=settings.openai_api_key)


def estimate_token_usage(text: str) -> int:
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def run_tts(text: str, voice: str = "alloy") -> str:
    """Генерирует речь и возвращает путь к файлу .wav"""
    text = text.strip()
    if len(text) < 3:
        raise ValueError("Text too short")
    if len(text) > 5000:
        raise ValueError("Text too long (max 5000 chars)")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        audio_path = tmp.name

    with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice=voice,
            response_format="wav",  # ✅ заменили format → response_format
            input=text
    ) as response:
        response.stream_to_file(audio_path)

    return audio_path
