import os
from datetime import datetime
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func, Integer, String, Text
from app.config import settings

DB_URL = settings.database_url

engine = create_async_engine(DB_URL, pool_pre_ping=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class RequestLog(Base):
    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    from_user: Mapped[str] = mapped_column(String(50), default="guest")  # потом можно заменить на user_id
    ip_address: Mapped[str] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    status: Mapped[str] = mapped_column(String(20))          # success | fail | rejected
    fail_reason: Mapped[str] = mapped_column(Text, nullable=True)

    token_used: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=True)

    file_size: Mapped[int] = mapped_column(Integer, nullable=True)
    file_type: Mapped[str] = mapped_column(String(50), nullable=True)
    detected_lang: Mapped[str] = mapped_column(String(20), nullable=True)

    api_model: Mapped[str] = mapped_column(String(50), default="gpt-4o-mini")

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
