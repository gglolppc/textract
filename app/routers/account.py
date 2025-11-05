from fastapi import Depends, Request, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db.database import User
from app.routers.auth.dependencies import get_current_user_or_none
from app.config.plans import TTS_PLAN_LIMITS, OCR_PLAN_LIMITS

from datetime import datetime

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
    }

    return templates.TemplateResponse(
        "account.html",
        {
            "request": request,
            "user": user_view,
            "plan_limit": {"ocr": plan_limit_ocr, "tts": plan_limit_tts},
        },
    )