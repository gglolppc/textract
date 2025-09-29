from fastapi import Depends, Request, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db.database import User
from app.routers.auth.dependencies import get_current_user_or_none
from app.config.plans import PLAN_LIMITS

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

    # Готовим плоские данные (строки/числа), никаких ORM-объектов
    created_at_str = (
        user.created_at.strftime("%Y-%m-%d") if getattr(user, "created_at", None) else "—"
    )
    expires_str = (
        user.expires.strftime("%Y-%m-%d") if getattr(user, "expires", None) else "—"
    )
    plan = user.subscription or "free"
    plan_limit = PLAN_LIMITS.get(plan, 0)

    user_view = {
        "id": user.id,
        "email": user.email,
        "subscription": plan,
        "requests": int(user.requests or 0),
        "created_at": created_at_str,
        "expires": expires_str,
    }

    return templates.TemplateResponse(
        "account.html",
        {
            "request": request,
            "user": user_view,
            "plan_limit": plan_limit,   # отдельно прокинем лимит, чтобы не лезть в мапу из шаблона
        },
    )
