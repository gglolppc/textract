import enum
from datetime import datetime
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import DateTime, func, Integer, String, Text, Boolean, ForeignKey, Enum
from app.config.config import settings
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import text

DB_URL = settings.database_url

engine = create_async_engine(DB_URL, pool_pre_ping=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class RoleEnum(str, enum.Enum):
    user = "user"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Авторизация
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum, name="role_enum", create_type=True),
        default=RoleEnum.user,
        nullable=False
    )
    status: Mapped[str] = mapped_column(String, default="active")      # active / banned
    provider: Mapped[str] = mapped_column(String, default="email")     # email / google / apple
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)

    # OTP
    otp_code: Mapped[Optional[str]] = mapped_column(String, nullable=True)   # одноразовый код (или hash)
    otp_salt: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    otp_expires: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    uuid_token : Mapped[str] = mapped_column(String, nullable=True)

    # Лимиты и подписки
    subscription: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # free / premium_monthly / premium_yearly
    sub_expires: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    # Учёт использования
    usage_count_ocr: Mapped[int] = mapped_column(Integer, default=0, nullable=True)  # сколько запросов сделал
    tts_usage: Mapped[int] = mapped_column(Integer, default=0, nullable=True)  # symbols
    usage_reset_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("NOW()"),  # гарантированно сработает в Postgres
        nullable=True
    )
    # Метаданные
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("NOW()"),  # гарантированно сработает в Postgres
        nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("NOW()"),  # дефолт при создании
        onupdate=func.now(),  # при UPDATE обновляется Python-уровнем
        nullable=True
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    requests: Mapped[list["RequestLog"]] = relationship(
        "RequestLog", back_populates="user", cascade="all, delete-orphan"
    )

class RequestLog(Base):
    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    ip_address: Mapped[str] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # --- статус выполнения ---
    status: Mapped[str] = mapped_column(String(20))  # success | fail | rejected
    fail_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # --- технические метрики ---
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer)
    api_model: Mapped[str] = mapped_column(String(50), default="gpt-4o-mini")

    # --- общий тип операции ---
    module: Mapped[str] = mapped_column(
        String(30),
        nullable=True,
        default="ocr"
    )  # ocr | translate | tts | audio_to_text

    # --- для TTS ---
    text_chars: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)   # сколько символов озвучено
    audio_duration: Mapped[Optional[float]] = mapped_column(Integer, nullable=True)  # длительность итогового аудио (сек)
    audio_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)   # размер файла в байтах
    voice_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # --- для OCR ---
    file_size: Mapped[Optional[int]] = mapped_column(Integer)
    file_type: Mapped[Optional[str]] = mapped_column(String(50))
    detected_lang: Mapped[Optional[str]] = mapped_column(String(20))

    # --- учёт токенов / символов ---
    token_used: Mapped[int] = mapped_column(Integer, default=0)

    # --- связь с пользователем ---
    user: Mapped["User"] = relationship("User", back_populates="requests")

class Feedback(Base):
    __tablename__ = "feedbacks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=True)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
