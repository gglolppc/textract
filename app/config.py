from pydantic_settings import BaseSettings, SettingsConfigDict
from app.paths import BASE_DIR
from typing import Optional


class Settings(BaseSettings):
    max_upload_mb: int = 10
    uploads_path: str = "uploads"
    allowed_origins: str = "http://127.0.0.1:5500"
    openai_api_key: str
    debug: bool = False
    local_test_image: Optional[str] = None
    database_url: str
    database_alembic_url: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8"
    )

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


settings = Settings()
