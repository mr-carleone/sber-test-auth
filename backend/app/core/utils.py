# app/core/utils.py
import base64
import logging
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes
from core.config import settings

logger = logging.getLogger(__name__)

def sign_data(data: str) -> str:
    try:
        logger.debug(f"Signing data: {data}")

        with open(settings.PRIVATE_KEY_PATH, "rb") as key_file:
            private_key: PrivateKeyTypes = load_pem_private_key(
                key_file.read(),
                password=None
            )

        signature: bytes = private_key.sign( # type: ignore
            data.encode(),
            padding.PKCS1v15(), # type: ignore
            hashes.SHA256() # type: ignore
        )
        return base64.b64encode(signature).decode() # type: ignore

    except Exception as e:
        logger.error(f"Error signing data: {e}")
        raise
