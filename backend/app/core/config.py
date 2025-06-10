# app/core/config.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

ENV_VALUE = os.getenv('ENV', 'dev')
ENV_FILE_PATH = f"/app/configs/.env.{ENV_VALUE}"

class Settings(BaseSettings):
    ENV: str = Field("dev", env="ENV")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    CLIENT_ID: str = Field(..., env="CLIENT_ID")
    CLIENT_SECRET: str = Field(..., env="CLIENT_SECRET")
    REDIRECT_URI: str = Field(..., env="REDIRECT_URI")
    PRIVATE_KEY_PATH: str = Field(..., env="PRIVATE_KEY_PATH")
    APP_HOST: str = Field("0.0.0.0", env="APP_HOST")
    APP_PORT: int = Field(8000, env="APP_PORT")

    # Конфигурация модели
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
        validate_assignment=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info(f"Environment: {self.ENV}")
        logger.info(f"Private key path: {self.PRIVATE_KEY_PATH}")

        # Проверка существования файла с приватным ключом
        key_path = Path(self.PRIVATE_KEY_PATH)
        if key_path.exists():
            logger.info("Private key file exists")
        else:
            logger.warning(f"Private key file does NOT exist at: {key_path}")

    @property
    def is_production(self):
        return self.ENV.lower() == "prod"

# Initialize settings
settings = Settings()
