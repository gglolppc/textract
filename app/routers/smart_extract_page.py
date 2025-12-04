from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, Depends

from app.routers.auth.dependencies import get_current_user_or_none
from app.db.database import User

router = APIRouter(prefix="/smart-extract", tags=["smart_extract"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def smart_extract_page(
    request: Request,
    user: User | None = Depends(get_current_user_or_none),
):
    if user:
        return templates.TemplateResponse("smart_extract.html", {
            "request": request,
            "user": user,
        })
    else:
        return templates.TemplateResponse("smart_extract.html", {
            "request": request
        })

