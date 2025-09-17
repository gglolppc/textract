from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from starlette.templating import Jinja2Templates

from app.db.database import User, get_session
from app.utils.security.otp_generator import generate_otp, hash_code, verify_otp
from app.schemas.user_create import UserCreate
from app.utils.security.jwt_handler import create_access_token, verify_access_token
from app.utils.security.send_mail import send_mail

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/register")
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
    if existing:
        raise HTTPException(400, "Email already registered")

    # создаём OTP
    otp_code, otp_expires = generate_otp()
    hashed_otp, salt = hash_code(otp_code)

    new_user = User(
        email=user_in.email,
        otp_code=hashed_otp,
        otp_salt=salt,
        otp_expires=otp_expires,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    await send_mail(new_user.email, "textract OTC confirmation code", otp_code)

    # редиректим на confirm с user_id
    return RedirectResponse(url=f"/auth/confirm?user_id={new_user.id}", status_code=303)


# Шаг 2. Страница подтверждения
@router.get("/confirm", response_class=HTMLResponse)
async def confirm_page(request: Request, user_id: int):
    # простая HTML форма
    return templates.TemplateResponse(
        "confirm.html", {"request": request, "user_id": user_id}
    )


@router.post("/confirm", response_class=HTMLResponse)
async def confirm_user(
    request: Request,
    user_id: int = Form(...),
    otp_code: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    user = await session.get(User, user_id)
    if not user:
        return templates.TemplateResponse(
            "confirm.html",
            {"request": request, "user_id": user_id, "error": "User not found"},
            status_code=404
        )

    if datetime.now(timezone.utc) > user.otp_expires:
        return templates.TemplateResponse(
            "confirm.html",
            {"request": request, "user_id": user_id, "error": "OTP expired"},
            status_code=400
        )

    if not verify_otp(user.otp_code, user.otp_salt, otp_code):
        return templates.TemplateResponse(
            "confirm.html",
            {"request": request, "user_id": user_id, "error": "Invalid code"},
            status_code=400
        )

    user.is_active = True
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
async def get_me(request: Request, session: AsyncSession = Depends(get_session)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(401, "Not authenticated")

    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(401, "Invalid token")

    try:
        user = await session.get(User, int(payload["sub"]))
    except Exception:
        # например, если БД упала
        raise HTTPException(500, "Database error")

    if not user:
        raise HTTPException(404, "User not found")

    return {"id": user.id, "email": user.email}

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")
    return response