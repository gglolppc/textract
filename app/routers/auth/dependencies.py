# dependencies.py
from fastapi import Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_session
from app.db.database import User
from app.utils.security.jwt_handler import verify_access_token



async def get_current_user_or_none(
    request: Request,
    session: AsyncSession = Depends(get_session)
) -> User | None:
    token = request.cookies.get("access_token")
    if not token:
        return None

    payload = verify_access_token(token)
    if not payload:
        return None

    user = await session.get(User, int(payload["sub"]))
    return user


async def require_current_user(
    user: User | None = Depends(get_current_user_or_none)
) -> User:
    if not user:
        raise HTTPException(401, "Not authenticated")
    return user


async def guest_only(user=Depends(get_current_user_or_none)):
    if user:
        # если уже залогинен → редиректим
        raise HTTPException(
            status_code=303,
            headers={"Location": "/"}  # на главную
        )