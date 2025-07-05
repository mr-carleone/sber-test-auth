import os
import uuid
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode

router = APIRouter(prefix="/api/v1/authorize", tags=["Sber OAuth Authorize"])

SBER_AUTH_URL = "https://efs-sbbol-ift-web.testsbi.sberbank.ru:9443/ic/sso/api/v1/oauth/authorize"
CLIENT_ID = os.getenv("CLIENT_ID")
REDIRECT_URI = os.getenv("REDIRECT_URI")
SCOPE = os.getenv("SCOPE", "openid")

@router.get("")
def get_authorize_url(request: Request):
    state = str(uuid.uuid4())
    nonce = uuid.uuid4().hex
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "state": state,
        "nonce": nonce,
        "prompt": "login"
    }
    query = urlencode(params)
    url = f"{SBER_AUTH_URL}?{query}"
    return RedirectResponse(url)
