from slowapi import Limiter
from fastapi import Request
from slowapi.wrappers import Limit

from app.utils.security.get_ip import get_client_ip

def fixed_is_exempt(self, request):
    return self.exempt_when(request) if self.exempt_when else False

Limit.is_exempt = fixed_is_exempt

limiter = Limiter(key_func=get_client_ip)

def exempt_authenticated(request: Request) -> bool:
    # если есть кука access_token → не лимитируем
    return bool(request.cookies.get("access_token"))