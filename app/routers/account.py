from fastapi import Depends, Request, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db.database import User
from app.routers.auth.dependencies import get_current_user_or_none
from app.config.plans import PLAN_LIMITS

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

    # Сразу вытаскиваем все нужные атрибуты
    user_data = {
        "id": user.id,
        "email": user.email,
        "requests": user.requests,
        "subscription": user.subscription,
    }

    return templates.TemplateResponse(
        "account.html",
        {
            "request": request,
            "user": user_data,   # <-- передаём dict, а не ORM
            "limits": PLAN_LIMITS,
        },
    )