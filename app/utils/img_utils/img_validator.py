from pathlib import Path

from PIL import Image
from io import BytesIO
from fastapi import HTTPException



def validate_image_file(scr: Path) -> None:
    """
    Проверяет, что изображение существует и доступно для чтения.
    """
    if not scr.exists() or not scr.is_file():
        raise HTTPException(400, "Upload error: image not saved")

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}

def is_image(raw: bytes) -> bool:
    try:
        Image.open(BytesIO(raw))
        return True
    except Exception:
        return False