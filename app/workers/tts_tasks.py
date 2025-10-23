from app.workers.celery_app import celery_app
from app.utils.tts.tts_query import run_tts

@celery_app.task(name="generate_tts_task")
def generate_tts_task(text: str, voice: str):
    """
    Выполняет TTS в фоне и возвращает путь к готовому файлу.
    """
    audio_path = run_tts(text, voice)
    return audio_path
