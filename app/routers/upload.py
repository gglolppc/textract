import traceback
from io import BytesIO
from PIL import Image
from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Form
from starlette.concurrency import run_in_threadpool
from app.utils.text_validator import has_text
from app.utils.ids import new_id
from app.config import settings
from app.paths import UPLOAD_DIR
from app.utils.img_validator import is_image, validate_image_url
from app.utils.ocr import run_ocr
from app.utils.limiter import limiter

router = APIRouter()

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}

@limiter.limit("3/day")
@router.post("/")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    language: str = Form("original")   # 👈 язык из формы
):
    max_bytes = settings.max_upload_mb * 1024 * 1024
    raw = await file.read()
    img = Image.open(BytesIO(raw)).convert("RGB")
    if not await run_in_threadpool(has_text, img):
        raise HTTPException(400, "File has no text")

    if len(raw) > max_bytes:
        raise HTTPException(400, "File too large")

    if not is_image(raw):
        raise HTTPException(400, "File is not a valid image")


    try:
        img = Image.open(BytesIO(raw)).convert("RGB")
        img.thumbnail((512, 512))

        uid = new_id()
        scr = (UPLOAD_DIR / f"{uid}.jpg").resolve()
        img.save(scr, format="JPEG", quality=95)
        link = f"https://textract.me/uploads/{uid}.jpg"
        validate_image_url(link)


        result = await run_in_threadpool(run_ocr, link, language)

        return {
            "text": result
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, f"Failed to process image: {e}")





