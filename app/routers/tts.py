from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.workers.celery_app import celery_app
from app.workers.tts_tasks import generate_tts_task
from app.utils.tts.spell_checker import is_meaningful_text

import os, tempfile

router = APIRouter(prefix="/text-to-speech", tags=["tts"])
templates = Jinja2Templates(directory="app/templates")

class TTSRequest(BaseModel):
    text: str
    voice: str | None = "alloy"


# 🟣 GET /tts/page — страница генерации речи
@router.get("/", response_class=HTMLResponse)
async def tts_page(request: Request):
    voices = ["alloy", "verse", "coral", "soft", "bright"]
    return templates.TemplateResponse(
        "tts_page.html",
        {"request": request, "voices": voices}
    )


# 🟣 POST /tts — генерация речи
@router.post("/")
async def generate_tts(data: TTSRequest):
    text = data.text.strip()
    if not text:
        return JSONResponse({"error": "Text cannot be empty."}, status_code=400)

    if not is_meaningful_text(text):
        return JSONResponse(
            {"error": "Text seems meaningless or unrecognized. Please enter real words."},
            status_code=400
        )

    try:
        task = generate_tts_task.delay(data.text, data.voice)
        return {
            "task_id": task.id,
            "status": "queued",
            "poll_url": f"/text-to-speech/status/{task.id}"
        }
    except Exception as e:
        return JSONResponse({"error": f"TTS failed: {e}"}, status_code=500)


@router.get("/status/{task_id}")
async def get_tts_status(task_id: str):
    task = celery_app.AsyncResult(task_id)

    if task.state == "PENDING":
        return {"status": "pending"}
    elif task.state == "STARTED":
        return {"status": "processing"}
    elif task.state == "SUCCESS":
        result = task.result
        filename = os.path.basename(result.get("audio_path", result))
        return {
            "status": "done",
            "audio_url": f"/text-to-speech/download/{filename}",
        }
    elif task.state == "FAILURE":
        return {"status": "error", "message": str(task.info)}

    return JSONResponse({"status": "unknown"}, status_code=404)

@router.get("/download/{filename}")
async def download_audio(filename: str):
    file_path = os.path.join("app/static/audio", filename)
    if not os.path.exists(file_path):
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(file_path, media_type="audio/wav", filename=filename)