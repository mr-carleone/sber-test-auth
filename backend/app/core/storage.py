# app/core/storage.py
import json
import os
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class TokenStorage:
    _instance = None
    FILE_PATH = Path(__file__).parent / 'token_data.json'

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__()
            cls._instance._load()
        return cls._instance

    def __init__(self):
        from core.config import settings
        self.settings = settings

        # Проверка прав доступа к файлу
        if self.FILE_PATH.exists():
            if not os.access(self.FILE_PATH, os.R_OK | os.W_OK):
                logger.error(f"Insufficient permissions for token file: {self.FILE_PATH}")

    def _load(self):
        if self.FILE_PATH.exists():
            logger.info(f"Loading token data from {self.FILE_PATH}")
            with open(self.FILE_PATH, 'r') as f:
                self.data = json.load(f)
        else:
            logger.info(f"Token file not found, creating new storage at {self.FILE_PATH}")
            self.data = {
                "access_token": "",
                "refresh_token": "",
                "expires_at": 0,
                "client_secret": self.settings.CLIENT_SECRET,
                "secret_expires_at": 0
            }
            self.save()

    def save(self):
        logger.info(f"Saving token data to {self.FILE_PATH}")
        with open(self.FILE_PATH, 'w') as f:
            json.dump(self.data, f, indent=2)

    def update_tokens(self, access_token: str, refresh_token: str, expires_in: int):
        self.data["access_token"] = access_token
        self.data["refresh_token"] = refresh_token
        self.data["expires_at"] = int(time.time()) + expires_in
        self.save()

    def update_client_secret(self, new_secret: str, expires_in: int = 40 * 24 * 3600):
        self.data["client_secret"] = new_secret
        self.data["secret_expires_at"] = int(time.time()) + expires_in
        self.save()

    @property
    def access_token(self) -> str:
        return str(self.data.get("access_token", ""))

    @property
    def refresh_token(self) -> str:
        return str(self.data.get("refresh_token", ""))

    @property
    def client_secret(self) -> str:
        from core.config import settings
        return str(self.data.get("client_secret", settings.CLIENT_SECRET))

    @property
    def access_token_expired(self) -> bool:
        return time.time() > float(self.data.get("expires_at", 0))

    @property
    def client_secret_expired(self) -> bool:
        return time.time() > float(self.data.get("secret_expires_at", 0))

    @property
    def client_secret_expires_soon(self) -> bool:
        # Предупреждение за 5 дней до истечения
        return time.time() > (float(self.data.get("secret_expires_at", 0)) - (5 * 24 * 3600))

storage = TokenStorage()
