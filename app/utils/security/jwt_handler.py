from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.config import settings

def create_access_token(data: dict, days: int = 365) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=days)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
