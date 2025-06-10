# app/routes/auth_routes.py
import os
import base64
import httpx
import logging
import time
from core.utils import sign_data
from fastapi import APIRouter, Request, HTTPException
from core.config import settings
from core.storage import storage


router = APIRouter() # сюда добавить api/v1 или вынести в системную переменную?? description
logger = logging.getLogger(__name__)

@router.get("/login")
async def login():
    logger.info("Generating login URL")
    return {
        "auth_url": f"https://api.sberbank.ru/ru/prod/oauth/authorize?"
        f"response_type=code&"
        f"client_id={settings.CLIENT_ID}&"
        f"redirect_uri={settings.REDIRECT_URI}"
    }

@router.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        logger.warning("Authorization code missing in callback")
        raise HTTPException(status_code=400, detail="Authorization code missing")

    logger.info(f"Received authorization code: {code[:5]}...")

    token_url = "https://api.sberbank.ru/ru/prod/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.REDIRECT_URI,
        "client_id": settings.CLIENT_ID
    }

    try:
        sorted_data = "&".join(f"{k}={v}" for k, v in sorted(data.items()))
        signature = sign_data(sorted_data)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_url,
                data=data,
                headers={
                    "X-Signature": signature,
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json"
                },
                timeout=10.0
            )

        logger.info(f"Token response status: {response.status_code}")
        token_data = response.json()
        storage.update_tokens(
            token_data["access_token"],
            token_data["refresh_token"],
            token_data["expires_in"]
        )
        return {"status": "tokens_updated", "expires_in": token_data["expires_in"]}

    except httpx.HTTPError as e:
        logger.error(f"HTTP error during token exchange: {e}")
        raise HTTPException(status_code=502, detail="Sber API unavailable")

# Добавим функцию для обновления токенов
async def refresh_access_token():
    logger.info("Refreshing access token")
    token_url = "https://api.sberbank.ru/ru/prod/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": storage.refresh_token,
        "client_id": settings.CLIENT_ID
    }

    sorted_data = "&".join(f"{k}={v}" for k, v in sorted(data.items()))
    signature = sign_data(sorted_data)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_url,
                data=data,
                headers={
                    "X-Signature": signature,
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json"
                },
                timeout=10.0
            )

        if response.status_code == 200:
            token_data = response.json()
            storage.update_tokens(
                token_data["access_token"],
                token_data["refresh_token"],
                token_data["expires_in"]
            )
            logger.info("Access token refreshed successfully")
            return True
        else:
            logger.error(f"Token refresh failed: {response.status_code} {response.text}")
            return False

    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        return False

async def update_client_secret():
    logger.info("Updating client secret")
    secret_url = "https://api.sberbank.ru/ru/prod/change-client-secret"

    data = {
        "client_id": settings.CLIENT_ID
    }

    sorted_data = "&".join(f"{k}={v}" for k, v in sorted(data.items()))
    signature = sign_data(sorted_data)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                secret_url,
                data=data,
                headers={
                    "X-Signature": signature,
                    "Authorization": f"Bearer {storage.access_token}",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json"
                },
                timeout=15.0
            )

        if response.status_code == 200:
            secret_data = response.json()
            new_secret = secret_data["new_client_secret"]
            storage.update_client_secret(new_secret)
            logger.info("Client secret updated successfully")
            return True
        else:
            logger.error(f"Client secret update failed: {response.status_code} {response.text}")
            return False

    except Exception as e:
        logger.error(f"Error updating client secret: {e}")
        return False
