import time
import traceback
from io import BytesIO
from PIL import Image
from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Form, Depends
from starlette.concurrency import run_in_threadpool

from app.config.plans import check_and_increment_usage
from app.routers.auth.dependencies import get_current_user_or_none
from app.utils.img_utils.text_validator import has_text
from app.utils.security.ids import new_id
from app.config.config import settings
from app.paths import UPLOAD_DIR
from app.utils.img_utils.img_validator import is_image, validate_image_file
from app.utils.img_utils.ocr import run_ocr
from app.utils.security.limiter import limiter, exempt_authenticated
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session, RequestLog, User
from app.utils.security.get_ip import get_client_ip

router = APIRouter()

@router.post("/")
@limiter.limit("5/day", exempt_when=exempt_authenticated)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    language: str = Form("original"),
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user_or_none)
):

    start_time = time.perf_counter()
    log_entry = RequestLog(
        ip_address=get_client_ip(request),
        user_id=user.id if user else None,
        status="pending"
    )
    session.add(log_entry)
    if user:
        check_and_increment_usage(user)
    await session.flush()

    max_bytes = settings.max_upload_mb * 1024 * 1024
    raw = await file.read()

    if len(raw) > max_bytes:
        log_entry.status = "failed"
        log_entry.fail_reason = "File too large"
        await session.commit()
        raise HTTPException(400, "File too large")

    if not is_image(raw):
        log_entry.status = "failed"
        log_entry.fail_reason = "File is not a valid image"
        await session.commit()
        raise HTTPException(400, "File is not a valid image")

    try:
        img = Image.open(BytesIO(raw)).convert("RGB")
        if not await run_in_threadpool(has_text, img):
            log_entry.status = "failed"
            log_entry.fail_reason = "File has no text"
            await session.commit()
            raise HTTPException(400, "File has no text")
        img.thumbnail((512, 512))

        uid = new_id()
        scr = (UPLOAD_DIR / f"{uid}.jpg").resolve()
        img.save(scr, format="JPEG", quality=95)
        validate_image_file(scr)

        link = f"https://textract.me/uploads/{uid}.jpg"
        if settings.debug and settings.local_test_image:
            link = settings.local_test_image

        result, tokens = await run_in_threadpool(run_ocr, link, language)

        log_entry.token_used = tokens
        log_entry.latency_ms = int((time.perf_counter() - start_time) * 1000)

        if result.status == "fail":
            return {"text": f"Fail to extract – {result.fail_reason}"}

        log_entry.status = "success"
        await session.commit()

        if language == "original":
            return {"text": result.extracted_text}
        else:
            return {"text": result.translated_text}

    except Exception as e:
        log_entry.status = "failed"
        log_entry.fail_reason = str(e)
        await session.commit()
        traceback.print_exc()
        raise HTTPException(500, f"Failed to process image: {e}")





