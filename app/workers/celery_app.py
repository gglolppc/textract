from celery import Celery
from app.config.config import settings

celery_app = Celery(
    "textract_tts",
    broker=settings.redis_url,    # пример: redis://localhost:6379/0
    backend=settings.redis_url
)

celery_app.conf.task_track_started = True
celery_app.conf.update(
    result_expires=3600,  # 1 час
)
