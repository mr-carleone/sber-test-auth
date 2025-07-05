from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/v1", tags=["Sber OAuth Callback"])

@router.get("/callback")
def sber_callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    return {"code": code, "state": state}
