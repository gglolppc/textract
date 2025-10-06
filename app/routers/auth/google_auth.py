from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config.config import settings
from app.db.database import get_session
from app.db.database import User
from app.utils.security.jwt_handler import create_access_token

router = APIRouter(prefix="/auth/google", tags=["auth"])

# Настройка OAuth
oauth = OAuth()
google = oauth.register(
    name="google",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    api_base_url="https://openidconnect.googleapis.com/v1/",
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/")
async def login_via_google(request: Request):
    redirect_uri = settings.google_redirect_uri
    print(redirect_uri)
    return await google.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def google_callback(request: Request, session: AsyncSession = Depends(get_session)):
    token = await google.authorize_access_token(request)
    # Получаем профиль через userinfo endpoint (надежно)
    resp = await google.get("userinfo", token=token)
    user_info = resp.json()

    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to fetch user info from Google")

    email = user_info.get("email")

    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        user = User(email=email, subscription="free")
        session.add(user)
        await session.commit()
        await session.refresh(user)

    access_token = create_access_token({"sub": str(user.id)})

    response = RedirectResponse(url="/account")
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return response
