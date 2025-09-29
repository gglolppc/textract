from slowapi import Limiter
from fastapi import Request

from app.utils.security.get_ip import get_client_ip

limiter = Limiter(key_func=get_client_ip)

def exempt_authenticated(request: Request) -> bool:
    # если есть кука access_token → не лимитируем
    return bool(request.cookies.get("access_token"))