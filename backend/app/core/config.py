# app/core/config.py
import os
from pydantic_settings import BaseSettings
from pydantic import HttpUrl, field_validator, computed_field
from typing import List, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # Основные настройки
    ENV: str = "dev"
    LOG_LEVEL: str = "INFO"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # OAuth настройки
    CLIENT_ID: str
    CLIENT_SECRET: str
    REDIRECT_URI: HttpUrl
    PRIVATE_KEY_PATH: str

    # Настройки безопасности
    ALLOWED_ORIGINS: List[str] = ["*"]
    RATE_LIMIT_PER_MINUTE: int = 60
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @computed_field
    @property
    def is_production(self) -> bool:
        return self.ENV.lower() == "prod"

    @field_validator("REDIRECT_URI", mode="before")
    @classmethod
    def validate_redirect_uri(cls, v: Any) -> HttpUrl:
        if isinstance(v, HttpUrl):
            return v
        return HttpUrl(v)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        logger.info(f"Environment: {self.ENV}")
        logger.info(f"Private key path: {self.PRIVATE_KEY_PATH}")

        # Проверка существования файла с приватным ключом
        key_path = Path(self.PRIVATE_KEY_PATH)
        if key_path.exists():
            logger.info("Private key file exists")
        else:
            logger.warning(f"Private key file does NOT exist at: {key_path}")

    class Config:
        env_file = f"/app/configs/.env.{os.getenv('ENV', 'dev')}"
        env_file_encoding = "utf-8"
        extra = "ignore"
        validate_assignment = True

# Initialize settings
settings = Settings()
