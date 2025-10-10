from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, status, Depends
from fastapi.responses import JSONResponse

from app.db.database import User
from app.routers.auth.dependencies import get_current_user_or_none

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

@router.get("/about", response_class=HTMLResponse)
async def about_page(request: Request,
                     user: User | None = Depends(get_current_user_or_none),):
    if user:
        return templates.TemplateResponse("about.html", {
            "request": request,
            "user": user,
        })
    else:
        return templates.TemplateResponse("about.html", {
            "request": request
        })

@router.get("/terms", response_class=HTMLResponse)
async def terms_page(request: Request,
                     user: User | None = Depends(get_current_user_or_none),):
    if user:
        return templates.TemplateResponse("terms.html", {
            "request": request,
            "user": user,
        })
    else:
        return templates.TemplateResponse("terms.html", {
            "request": request
        })

@router.get("/privacy", response_class=HTMLResponse)
async def privacy_page(request: Request,
                       user: User | None = Depends(get_current_user_or_none),):
    if user:
        return templates.TemplateResponse("privacy.html", {
            "request": request,
            "user": user,
        })
    else:
        return templates.TemplateResponse("privacy.html", {
            "request": request
        })

@router.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request,
                       user: User | None = Depends(get_current_user_or_none),):
    if user:
        return templates.TemplateResponse("contact.html", {
            "request": request,
            "user": user,
        })
    else:
        return templates.TemplateResponse("contact.html", {
            "request": request
        })

api_router = APIRouter(prefix="/api")

@api_router.post("/contact")
async def send_contact_message(request: Request):
    data = await request.json()
    email = data.get("email")
    message = data.get("message")

    # Здесь можешь подключить email отправку, Telegram-бот или запись в БД
    print(f"[CONTACT] From: {email} — {message}")

    return JSONResponse({"status": "ok"}, status_code=status.HTTP_200_OK)