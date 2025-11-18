from fastapi import Depends, Request, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import User, get_session, RequestLog
from app.routers.auth.dependencies import get_current_user_or_none
from app.config.plans import TTS_PLAN_LIMITS, OCR_PLAN_LIMITS
from sqlalchemy import select
from datetime import datetime
import asyncio
from fastapi.responses import FileResponse

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/account", tags=["account"])

@router.get("/", response_class=HTMLResponse)
async def account_page(
    request: Request,
    user: User = Depends(get_current_user_or_none)
):
    if not user:
        response = RedirectResponse("/auth/register", status_code=303)
        response.delete_cookie("access_token")
        return response

    plan = user.subscription or "free"
    plan_limit_tts = TTS_PLAN_LIMITS.get(plan, 0)
    plan_limit_ocr = OCR_PLAN_LIMITS.get(plan, 0)

    user_view = {
        "id": user.id,
        "email": user.email,
        "subscription": plan,
        "requests_ocr": user.usage_count_ocr,   # <-- берём счётчик, а не relationship
        "requests_tts": user.tts_usage,
        "created_at": (
            user.created_at.strftime("%Y-%m-%d") if user.created_at else "—"
        ),
        "expires": (
            user.sub_expires.strftime("%Y-%m-%d") if user.sub_expires else "—"
        ),
        "last_login_at":(
            user.last_login_at.strftime('%d/%m/%Y %H:%M:%S') if user.last_login_at else "—"
        ),
    }

    return templates.TemplateResponse(
        "account.html",
        {
            "request": request,
            "user": user_view,
            "plan_limit": {"ocr": plan_limit_ocr, "tts": plan_limit_tts},
        },
    )

@router.get("/history", response_class=HTMLResponse)
async def account_history(
        request: Request,
        user: User = Depends(get_current_user_or_none),
        session: AsyncSession = Depends(get_session),
):
    if not user:
        response = RedirectResponse("/auth/register", status_code=303)
        response.delete_cookie("access_token")
        return response
    if user.subscription == "free":
        return templates.TemplateResponse("account_history_free.html", {
            "request": request,
            "user": user,
        })
    ocr_query = select(RequestLog).where(
        RequestLog.user_id == user.id,
        RequestLog.module == "ocr"
    ).order_by(RequestLog.created_at.desc())

    # --- TTS ---
    tts_query = select(RequestLog).where(
        RequestLog.user_id == user.id,
        RequestLog.module == "tts"
    ).order_by(RequestLog.created_at.desc())

    ocr_logs = (await session.scalars(ocr_query)).all()
    tts_logs = (await session.scalars(tts_query)).all()

    return templates.TemplateResponse("account_history.html", {
        "request": request,
        "user": user,
        "ocr_logs": ocr_logs,
        "tts_logs": tts_logs
    })

from fastapi import  Depends, HTTPException
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


PRIVATE_OCR_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../private/ocr_pdf")
)
os.makedirs(PRIVATE_OCR_DIR, exist_ok=True)

@router.post("/history/generate-pdf/{log_id}")
async def generate_pdf(
    log_id: int,
    user: User = Depends(get_current_user_or_none),
    session: AsyncSession = Depends(get_session),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authorized")

    # --- достаём запись ---
    stmt = select(RequestLog).where(
        RequestLog.id == log_id,
        RequestLog.user_id == user.id
    )
    result = await session.execute(stmt)
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Request not found")

    if not log.extracted_text:
        raise HTTPException(status_code=400, detail="No text available for PDF")

    # --- если уже существует ---
    if log.pdf_link:
        return {
            "status": "exists",
            "pdf_url": f"/account/download/pdf/{log.id}"
        }

    # --- готовим путь ---
    user_folder = os.path.join(PRIVATE_OCR_DIR, f"user_{user.id}")
    os.makedirs(user_folder, exist_ok=True)

    pdf_name = f"ocr_{log_id}.pdf"
    pdf_path = os.path.join(user_folder, pdf_name)

    # --- генерация PDF ---
    async def create_pdf(path: str, text: str):
        def _sync_pdf():
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont

            # ✅ Unicode шрифт (чтобы не было квадратов)
            font_path = os.path.join(os.path.dirname(__file__), "../../static/fonts/DejaVuSans.ttf")
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
                font_name = "DejaVuSans"
            else:
                font_name = "Helvetica"

            c = canvas.Canvas(path, pagesize=A4)
            text_obj = c.beginText(40, 800)
            text_obj.setFont(font_name, 11)

            for line in text.splitlines():
                text_obj.textLine(line)

            c.drawText(text_obj)
            c.save()

        return await asyncio.to_thread(_sync_pdf)

    await create_pdf(pdf_path, log.extracted_text)

    # --- сохраняем относительный путь ---
    log.pdf_link = f"user_{user.id}/{pdf_name}"
    await session.commit()

    # --- возвращаем ссылку ---
    return {
        "status": "ok",
        "pdf_url": f"/account/download/pdf/{log.id}"
    }


@router.get("/download/pdf/{log_id}")
async def download_ocr_pdf(
    log_id: int,
    user: User = Depends(get_current_user_or_none),
    session: AsyncSession = Depends(get_session)
):
    # достаём запись
    stmt = select(RequestLog).where(RequestLog.id == log_id)
    result = await session.execute(stmt)
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(status_code=404, detail="Record not found")

    # проверяем владельца
    if log.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # проверяем файл
    file_path = os.path.join(PRIVATE_OCR_DIR, log.pdf_link)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=410, detail="File missing")

    return FileResponse(file_path, media_type="application/pdf", filename=os.path.basename(file_path))