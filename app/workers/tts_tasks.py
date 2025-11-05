from app.workers.celery_app import celery_app
from app.utils.tts.tts_query import run_tts

@celery_app.task(name="generate_tts_task")
def generate_tts_task(text: str, voice: str):
    try:
        result = run_tts(text, voice)
        result["status"] = "success"
        return result
    except Exception as e:
        return {"status": "fail", "error": str(e)}
