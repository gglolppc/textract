import time

from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import RequestLog, User, get_session
from app.routers.auth.dependencies import get_current_user_or_none
from app.utils.security.get_ip import get_client_ip
from app.workers.celery_app import celery_app
from app.workers.tts_tasks import generate_tts_task
from app.utils.tts.spell_checker import is_meaningful_text
from app.config.plans import TTS_PLAN_LIMITS, increment_tts_usage

import os, tempfile

MAX_TTS_CHARS = 8000

router = APIRouter(prefix="/text-to-speech", tags=["tts"])
templates = Jinja2Templates(directory="app/templates")

class TTSRequest(BaseModel):
    text: str
    voice: str | None = "alloy"


# 🟣 GET /tts/page — страница генерации речи
@router.get("/", response_class=HTMLResponse)
async def tts_page(request: Request,
                   user: User | None = Depends(get_current_user_or_none)):
    voices = {
        "alloy": "Alex — balanced neutral",
        "echo": "Liam — energetic male",
        "fable": "Emma — expressive female",
        "onyx": "Daniel — deep velvet male",
        "nova": "Sofia — lively female",
        "shimmer": "Grace — warm female",
        "coral": "Hana — calm natural female",
        "verse": "Michael — announcer male",
        "ballad": "Ethan — smooth steady male",
        "ash": "Noah — serious low male",
        "sage": "Oliver — confident male",
        "marin": "Luna — friendly female",
        "cedar": "Eli — gentle male",
    }

    if user:
        return templates.TemplateResponse("tts_page.html", {
            "request": request,
            "user": user,
            "voices": voices,
            "plans": TTS_PLAN_LIMITS,
        })
    else:
        return templates.TemplateResponse("tts_page.html", {
            "request": request,
            "voices": voices,
            "plans": TTS_PLAN_LIMITS,
        })


# 🟣 POST /tts — генерация речи
@router.post("/")
async def generate_tts(
    data: TTSRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user_or_none)
):
    start_time = time.perf_counter()

    # --- Авторизация ---
    if not user:
        return JSONResponse({"error": "Please log in to use text-to-speech."}, status_code=401)

    # --- Подписка и лимиты ---
    plan = user.subscription or "free"
    plan_limit = TTS_PLAN_LIMITS.get(plan, TTS_PLAN_LIMITS["free"])
    max_char = plan_limit["max_char"]
    total_limit = plan_limit["total_char"]

    # --- Подготовка текста ---
    text = data.text.strip()
    if not text:
        return JSONResponse({"error": "Text cannot be empty."}, status_code=400)
    if not is_meaningful_text(text):
        return JSONResponse(
            {"error": "Text seems meaningless or unrecognized. Please enter real words."},
            status_code=400
        )

    # --- Подсчёт символов ---
    char_count = sum(1 for ch in text if ch.isprintable())

    # --- Проверка разового лимита ---
    if char_count > max_char:
        return JSONResponse(
            {"error": f"Text too long (max {max_char} characters per request)."},
            status_code=400
        )

    # --- Проверка и обновление месячного лимита ---
    increment_tts_usage(user, char_count)

    # --- Лог запроса ---
    log_entry = RequestLog(
        ip_address=get_client_ip(request),
        user_id=user.id,
        status="queued",
        module="tts",
        api_model="gpt-4o-mini-tts",
        text_chars=char_count,
        token_used=char_count,
        latency_ms=int((time.perf_counter() - start_time) * 1000)
    )
    session.add(log_entry)
    await session.commit()

    # --- Отправляем задачу в Celery ---
    try:
        task = generate_tts_task.delay(text, data.voice)
        return {
            "task_id": task.id,
            "status": "queued",
            "poll_url": f"/text-to-speech/status/{task.id}",
            "chars_used": char_count,
            "limit_total": total_limit,
            "used_total": user.tts_usage
        }

    except Exception as e:
        log_entry.status = "fail"
        log_entry.fail_reason = str(e)
        await session.commit()
        return JSONResponse({"error": f"TTS failed: {e}"}, status_code=500)



@router.get("/status/{task_id}")
async def get_tts_status(task_id: str):
    task = generate_tts_task.AsyncResult(task_id)

    if task.state == "PENDING":
        return {"status": "queued"}
    elif task.state == "STARTED":
        return {"status": "processing"}
    elif task.state == "SUCCESS":
        result = task.result
        return {
            "status": "done",
            "audio_url": result["url"],
            "filename": result["filename"]
        }
    elif task.state == "FAILURE":
        return {"status": "error", "message": str(task.info)}
    else:
        return {"status": task.state.lower()}

@router.get("/download/{filename}")
async def download_audio(filename: str):
    file_path = os.path.join("app/static/audio", filename)
    if not os.path.exists(file_path):
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(file_path, media_type="audio/wav", filename=filename)