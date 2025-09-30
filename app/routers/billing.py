from fastapi import Depends, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.db.database import User
from app.routers.auth.dependencies import get_current_user_or_none

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/billing", tags=["billing"])

@router.get("/", response_class=HTMLResponse)
async def billing_page(
    request: Request,
    user: User | None = Depends(get_current_user_or_none),
):
    if user:
        return templates.TemplateResponse("billing.html", {
            "request": request,
            "user": user,
        })
    else:
        return templates.TemplateResponse("billing.html", {
            "request": request
        })
