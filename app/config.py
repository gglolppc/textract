from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.paths import BASE_DIR


class Settings(BaseSettings):
    max_upload_mb: int = 10
    uploads_path: Path = Path("./uploads")
    allowed_origins: List[str] = ["http://127.0.0.1:5500"]
    openai_api_key: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8"
    )

settings = Settings()