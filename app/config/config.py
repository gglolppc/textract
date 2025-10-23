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
    jwt_secret: str
    jwt_algorithm: str
    smtp_user: str
    smtp_password: str
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_from: str = "<EMAIL>"
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    session_secret: str
    redis_url: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8"
    )

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


settings = Settings()
