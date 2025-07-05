import uuid
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from app.core.config import settings

router = APIRouter(prefix="/api/v1/authorize", tags=["Sber OAuth Authorize"])

@router.get("")
def get_authorize_url(request: Request):
    state = str(uuid.uuid4())
    nonce = str(uuid.uuid4())
    params = {
        "response_type": "code",
        "client_id": settings.CLIENT_ID,
        "redirect_uri": settings.REDIRECT_URI,
        "scope": settings.SCOPE,
        "state": state,
        "nonce": nonce,
        "prompt": "login"
    }
    url = f"{settings.SBER_AUTH_URL}?{urlencode(params, safe=' ')}"
    return RedirectResponse(url)
