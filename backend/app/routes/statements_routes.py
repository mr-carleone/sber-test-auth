# app/routes/statements_routes.py
from fastapi import APIRouter, HTTPException
import httpx
import logging
from core.storage import storage
from core.config import settings
from core.utils import sign_data

router = APIRouter() # сюда добавить api/v1 или вынести в системную переменную?? description
logger = logging.getLogger(__name__)

@router.get("/transactions")
async def get_transactions(accountNumber: str, fromDate: str, toDate: str):
    # Проверка токена
    if not storage.access_token or storage.access_token_expired:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")

    # Формирование запроса
    base_url = "https://api.sberbank.ru/ru/prod/statement/transactions"
    params = {
        "accountNumber": accountNumber,
        "fromDate": fromDate,
        "toDate": toDate
    }

    # Подпись параметров
    sorted_params = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    signature = sign_data(sorted_params)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                base_url,
                params=params,
                headers={
                    "X-Signature": signature,
                    "Authorization": f"Bearer {storage.access_token}",
                    "Accept": "application/json"
                },
                timeout=30.0
            )

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Transactions request failed: {response.status_code} {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Failed to get transactions")

    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
