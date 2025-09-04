from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.paths import BASE_DIR


class Settings(BaseSettings):
    max_upload_mb: int = 10
    uploads_path: str = "uploads"
    allowed_origins: List[str] = []
    openai_api_key: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8"
    )

settings = Settings()