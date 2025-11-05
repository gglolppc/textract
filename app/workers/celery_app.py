from celery import Celery
from app.config.config import settings

celery_app = Celery(
    "textract_tts",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tts_tasks"],  # 👈 вот эта строка
)

celery_app.conf.task_track_started = True
celery_app.conf.update(result_expires=3600)
