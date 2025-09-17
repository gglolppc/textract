import hmac
import secrets
from datetime import datetime, timedelta, timezone
import hashlib, secrets

def hash_code(code: str, salt: str | None = None) -> tuple[str, str]:
    if not salt:
        salt = secrets.token_hex(16)  # 32 символа случайной соли
    hash_val = hashlib.sha256((salt + code).encode()).hexdigest()
    return hash_val, salt

def generate_otp(length: int = 6, ttl_minutes: int = 5):
    otp = "".join(secrets.choice("0123456789") for _ in range(length))
    expires = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)
    return otp, expires

def verify_otp(stored_hash: str, stored_salt: str, input_code: str) -> bool:
    hash_val = hashlib.sha256((stored_salt + input_code).encode()).hexdigest()
    return hmac.compare_digest(hash_val, stored_hash)