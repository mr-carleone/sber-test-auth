# app/core/utils.py
import os
import base64
import logging
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from core.config import settings

logger = logging.getLogger(__name__)

def sign_data(data: str) -> str:
    try:
        logger.debug(f"Signing data: {data}")

        with open(settings.PRIVATE_KEY_PATH, "rb") as key_file:
            private_key = load_pem_private_key(
                key_file.read(),
                password=None
            )

        signature = private_key.sign(
            data.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode()

    except Exception as e:
        logger.error(f"Error signing data: {e}")
        raise
