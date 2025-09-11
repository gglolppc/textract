from fastapi import APIRouter, Request, Form
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session, Feedback
from app.utils.limiter import limiter

router = APIRouter()

@router.post("/feedback")
@limiter.limit("5/hour")
async def feedback(
        request: Request,
        user_feedback: str = Form(...),
        session: AsyncSession = Depends(get_session)
):
    new_feedback = Feedback(text=user_feedback)
    session.add(new_feedback)
    await session.commit()

