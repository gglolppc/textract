from PIL import Image
from io import BytesIO
import httpx
from fastapi import HTTPException



def validate_image_url(url: str):
    try:
        r = httpx.get(url, timeout=5)
        if r.status_code != 200:
            raise HTTPException(400, "Upload error: image not accessible")
    except Exception:
        raise HTTPException(400, "Upload error: invalid image link")

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}

def is_image(raw: bytes) -> bool:
    try:
        Image.open(BytesIO(raw))
        return True
    except Exception:
        return False