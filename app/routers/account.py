from fastapi import Depends, Request, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db.database import User
from app.routers.auth.dependencies import get_current_user_or_none
from app.config.plans import PLAN_LIMITS

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/account", tags=["account"])

@router.get("/account")
async def account_page(request: Request, user: User = Depends(get_current_user_or_none)):
    if not user:
        response = RedirectResponse("/auth/register", status_code=303)
        response.delete_cookie("access_token")
        return response
    return templates.TemplateResponse("account.html", {"request": request, "user": user, "limits" : PLAN_LIMITS})