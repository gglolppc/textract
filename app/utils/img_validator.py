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
    # в серый формат
    gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)

    # лёгкий threshold для выделения текста
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    text = pytesseract.image_to_string(thresh)
    return len(text.strip()) >= min_chars