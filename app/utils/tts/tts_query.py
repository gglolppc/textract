from openai import OpenAI
import tempfile
from app.config.config import settings
import tiktoken
import os

client = OpenAI(api_key=settings.openai_api_key)
STATIC_TTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../static/tts")
)
os.makedirs(STATIC_TTS_DIR, exist_ok=True)

def estimate_token_usage(text: str) -> int:
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def run_tts(text: str, voice: str = "alloy") -> dict:
    """Генерирует речь и возвращает путь и имя файла"""
    text = text.strip()
    if len(text) < 3:
        raise ValueError("Text too short")
    if len(text) > 5000:
        raise ValueError("Text too long (max 5000 chars)")

    filename = f"tts_{voice}_{hash(text)}.wav"
    audio_path = os.path.join(STATIC_TTS_DIR, filename)

    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice=voice,
        response_format="wav",
        input=text
    ) as response:
        response.stream_to_file(audio_path)

    return {
        "audio_path": audio_path,
        "filename": filename,
        "url": f"/static/tts/{filename}"
    }
