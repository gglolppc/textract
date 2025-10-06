from datetime import timezone, datetime
from fastapi import HTTPException
from dateutil.relativedelta import relativedelta
from app.db.database import User

PLAN_LIMITS = {
    "free": {"limit": 10, "period": "week"},
    "premium_monthly": {"limit": 10000, "period": "month"},
    "premium_yearly": {"limit": None, "period": "year"},  # unlimited
}

def check_and_increment_usage(user: User):
    plan = PLAN_LIMITS[user.subscription]
    limit, period = plan["limit"], plan["period"]

    now = datetime.now(timezone.utc)

    # сброс, если прошло время
    if user.usage_reset_at is None or now > user.usage_reset_at:
        user.usage_count = 0
        if period == "month":
            user.usage_reset_at = now + relativedelta(months=1)
        elif period == "year":
            user.usage_reset_at = now + relativedelta(years=1)
        elif period == "week":
            user.usage_reset_at = now + relativedelta(weeks=1)


    # проверка лимита
    if limit is not None and user.usage_count >= limit:
        raise HTTPException(
            status_code=402,
            detail="Update your account to premium"
        )

    # увеличиваем
    user.usage_count += 1

