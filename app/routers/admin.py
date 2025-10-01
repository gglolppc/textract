# app/routers/admin.py
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from starlette.responses import HTMLResponse

from app.db.database import get_session, User, RequestLog, Feedback, RoleEnum
from app.routers.auth.dependencies import get_current_user_or_none  # предполагается, что возвращает User model

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/adm", tags=["admin"])

async def require_admin(user = Depends(get_current_user_or_none)):
    # user должен быть объектом User из БД
    if not user or getattr(user, "role", None) != RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    return user

@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request,
                          session: AsyncSession = Depends(get_session),
                          user = Depends(require_admin)):

    requests = (await session.execute(
        select(RequestLog).order_by(RequestLog.created_at.desc()).limit(20)
    )).scalars().all()
    feedbacks = (await session.execute(
        select(Feedback).limit(20)
    )).scalars().all()
    users = (await session.execute(
        select(User).order_by(User.created_at.desc()).limit(20)
    )).scalars().all()
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "user": user,
        "requests": requests,
        "feedbacks": feedbacks,
        "users": users
    })
