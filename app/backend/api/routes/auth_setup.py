"""Authentication setup endpoint."""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from config import CONFIG_AUTH_CLIENT

router = APIRouter()


@router.get("/auth-setup",tags=["AuthSetup"])
async def auth_setup(request: Request):
    cfg = getattr(request.app.state, "config", None)
    if cfg is None:
        raise HTTPException(status_code=503, detail="App not initialized")

    auth_client = cfg.get(CONFIG_AUTH_CLIENT)
    if auth_client is None:
        raise HTTPException(status_code=503, detail="Auth client not configured")

    setup_info = auth_client.get_auth_setup_for_client()
    return JSONResponse(setup_info)
