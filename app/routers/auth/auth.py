from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from starlette.templating import Jinja2Templates

from app.db.database import User, get_session
from app.routers.auth.dependencies import guest_only, require_current_user
from app.utils.security.ids import new_id
from app.utils.security.otp_generator import generate_otp, hash_code, verify_otp
from app.schemas.user_create import UserCreate
from app.utils.security.jwt_handler import create_access_token
from app.utils.security.send_mail import send_mail

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/register", dependencies=[Depends(guest_only)])
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Шаг 1. Регистрация
@router.post("/register")
async def register_user(
    email: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    user_in = UserCreate(email=email)

    # проверяем дубликаты
    existing = await session.scalar(select(User).where(User.email == user_in.email))

    # создаём OTP
    otp_code, otp_expires = generate_otp()
    hashed_otp, salt = hash_code(otp_code)
    uuid_token = new_id()
    if not existing:
        user = User(
            email=user_in.email,
            otp_code=hashed_otp,
            otp_salt=salt,
            otp_expires=otp_expires,
            uuid_token=uuid_token,
            subscription = "free",
            usage_reset_at = None
        )
        session.add(user)
    else:
        user = existing
        user.is_active = False
        user.otp_code = hashed_otp
        user.otp_salt = salt
        user.otp_expires = otp_expires
        user.uuid_token = uuid_token
        user.updated_at = datetime.now(timezone.utc)
        user.last_login_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(user)
    await send_mail(user.email, "textract OTP confirmation code", otp_code)

    # редиректим на confirm
    return RedirectResponse(url=f"/auth/confirm?token={uuid_token}", status_code=303)

# Шаг 2. Страница подтверждения
@router.get("/confirm", response_class=HTMLResponse, dependencies=[Depends(guest_only)])
async def confirm_page(request: Request,
                       token: str,
                       session: AsyncSession = Depends(get_session)):
    user = await session.scalar(select(User).where(User.uuid_token == token))
    if not user:
        raise HTTPException(404, "Invalid link")
    # простая HTML форма
    return templates.TemplateResponse(
        "confirm.html", {"request": request, "token": token}
    )


@router.post("/confirm", response_class=HTMLResponse)
async def confirm_user(
    request: Request,
    token: str = Form(...),
    otp_code: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    user = await session.scalar(select(User).where(User.uuid_token == token))
    if not user:
        return templates.TemplateResponse(
            "confirm.html",
            {"request": request, "token": token, "error": "User not found"},
            status_code=404
        )

    if datetime.now(timezone.utc) > user.otp_expires:
        return templates.TemplateResponse(
            "confirm.html",
            {"request": request, "token": token, "error": "OTP expired"},
            status_code=400
        )

    if not verify_otp(user.otp_code, user.otp_salt, otp_code):
        return templates.TemplateResponse(
            "confirm.html",
            {"request": request, "token": token, "error": "Invalid code"},
            status_code=400
        )

    user.is_active = True
    user.uuid_token = ""
    await session.commit()

    # 1. создаём JWT
    token = create_access_token({"sub": str(user.id)})

    # 2. редиректим на главную и ставим куку
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,   # чтобы JS не мог читать
        secure=True,    # True если https
        samesite="lax"
    )
    return response




@router.get("/me")
async def get_me(user: User = Depends(require_current_user)):
    return {"id": user.id, "email": user.email}

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")
    return response