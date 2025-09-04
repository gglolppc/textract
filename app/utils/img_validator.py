from PIL import Image
from io import BytesIO
import httpx
from fastapi import HTTPException
import cv2
import pytesseract
import numpy as np

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


def has_text(img: Image.Image, min_chars: int = 5) -> bool:
    gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)

    config = "--oem 3 --psm 6"
    text = pytesseract.image_to_string(gray, config=config)

    return len(text.strip()) >= min_chars