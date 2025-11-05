from datetime import timezone, datetime
from fastapi import HTTPException
from dateutil.relativedelta import relativedelta
from app.db.database import User

OCR_PLAN_LIMITS = {
    "free": {"limit": 30, "period": "month"},
    "premium": {"limit": 10000, "period": "month"},
    "pro": {"limit": None, "period": "month"},  # unlimited
}

TTS_PLAN_LIMITS = {
    "free": {"max_char": 200, "total_char": 5000},
    "premium": {"max_char": 8000, "total_char": 100000},
    "pro": {"max_char": 18000, "total_char": 500000},
}

def _next_reset_at(now: datetime, period: str) -> datetime:
    if period == "week":
        return now + relativedelta(weeks=1)
    if period == "year":
        return now + relativedelta(years=1)
    # default = month
    return now + relativedelta(months=1)

def check_and_increment(
    user,
    plan_limits: dict,
    usage_field: str,
    *,
    increment_by: int = 1,
    limit_key: str = "limit",
    now: datetime | None = None,
):
    """
    Универсальная проверка/инкремент usage.
    - usage_field: имя поля в User (например, 'usage_count' или 'tts_usage')
    - increment_by: на сколько увеличить (для OCR = 1, для TTS = char_count)
    - limit_key: какое поле в plan_limits считать потолком ('limit' для OCR, 'total_char' для TTS)
    """
    if increment_by <= 0:
        return  # нечего инкрементировать

    if now is None:
        now = datetime.now(timezone.utc)

    subscription = (user.subscription or "free")
    plan = plan_limits.get(subscription) or plan_limits.get("free")
    if plan is None:
        raise HTTPException(500, "Plan limits not configured")

    period = plan.get("period", "month")
    limit = plan.get(limit_key, None)  # может быть None (безлимит)

    # сброс при истечении периода (общая дата для всех счётчиков — как у тебя)
    if user.usage_reset_at is None or now >= user.usage_reset_at:
        # Сбрасываем только конкретное поле usage_field (чтобы другие счетчики не трогать)
        setattr(user, usage_field, 0)
        user.usage_reset_at = _next_reset_at(now, period)

    current = getattr(user, usage_field, 0) or 0
    if limit is not None and (current + increment_by) > limit:
        # 402 — как у тебя, можно 403 если хочется "forbidden"
        raise HTTPException(status_code=402, detail="Usage limit reached. Upgrade your plan to continue.")

    setattr(user, usage_field, current + increment_by)


# 🔹 Удобные врапперы

def increment_ocr_usage(user):
    """
    OCR: считает по штукам (1 изображение/1 запрос).
    Предполагает, что OCR_PLAN_LIMITS[plan] содержит:
      - limit: максимальное кол-во запросов за период
      - period: 'week' | 'month' | 'year'
    """
    check_and_increment(
        user,
        plan_limits=OCR_PLAN_LIMITS,
        usage_field="usage_count_ocr",
        increment_by=1,
        limit_key="limit",
    )


def increment_tts_usage(user, char_count: int):
    """
    TTS: считает по символам.
    Предполагает, что TTS_PLAN_LIMITS[plan] содержит:
      - total_char: месячный лимит символов
      - max_char: разовый лимит (проверять отдельно в эндпоинте)
      - period: обычно 'month'
    """
    if char_count <= 0:
        return
    check_and_increment(
        user,
        plan_limits=TTS_PLAN_LIMITS,
        usage_field="tts_usage",
        increment_by=char_count,
        limit_key="total_char",
    )