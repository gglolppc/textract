from datetime import datetime
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func, Integer, String, Text, Boolean
from app.config import settings
from sqlalchemy.dialects.postgresql import TIMESTAMP

DB_URL = settings.database_url

engine = create_async_engine(DB_URL, pool_pre_ping=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Авторизация
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String, default="user")          # user / admin
    status: Mapped[str] = mapped_column(String, default="active")      # active / banned
    provider: Mapped[str] = mapped_column(String, default="email")     # email / google / apple
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)

    # OTP
    otp_code: Mapped[Optional[str]] = mapped_column(String, nullable=True)   # одноразовый код (или hash)
    otp_salt: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    otp_expires: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    # Лимиты и подписки
    tokens: Mapped[int] = mapped_column(Integer, default=5)
    subscription: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # free / basic / pro / unlimited
    sub_expires: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    # Метаданные
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

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

class Feedback(Base):
    __tablename__ = "feedbacks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=True)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
