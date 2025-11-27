"""Ask and chat endpoints (including NDJSON streaming)."""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse

from config import (
    CONFIG_ASK_APPROACH,
    CONFIG_CHAT_APPROACH,
    CONFIG_CHAT_HISTORY_BROWSER_ENABLED,
    CONFIG_CHAT_HISTORY_COSMOS_ENABLED,
    CONFIG_COSMOS_HISTORY_CONTAINER,
    CONFIG_COSMOS_HISTORY_VERSION,
)
from .utils import ndjson_bytes
from ..dependencies import get_auth_claims

router = APIRouter()


@router.post("/ask")
async def ask(request: Request, auth_claims: dict = Depends(get_auth_claims)):
    if request.headers.get("content-type", "").find("application/json") == -1:
        return JSONResponse({"error": "request must be json"}, status_code=415)
    body = await request.json()
    context = body.get("context", {}) or {}
    context["auth_claims"] = auth_claims
    try:
        approach = request.app.state.config.get(CONFIG_ASK_APPROACH)
        if approach is None:
            return JSONResponse({"error": "Ask approach not configured"}, status_code=503)
        r = await approach.run(body["messages"], context=context, session_state=body.get("session_state"))
        return JSONResponse(r)
    except Exception as error:
        return JSONResponse({"error": str(error)}, status_code=500)


@router.post("/chat/stream")
async def chat_stream(request: Request, auth_claims: dict = Depends(get_auth_claims)):
    if request.headers.get("content-type", "").find("application/json") == -1:
        return JSONResponse({"error": "request must be json"}, status_code=415)
    body = await request.json()
    context = body.get("context", {}) or {}
    context["auth_claims"] = auth_claims
    try:
        approach = request.app.state.config.get(CONFIG_CHAT_APPROACH)
        if approach is None:
            return JSONResponse({"error": "Chat approach not configured"}, status_code=503)

        session_state = body.get("session_state")
        if session_state is None:
            from core.sessionhelper import create_session_id

            session_state = create_session_id(
                request.app.state.config.get(CONFIG_CHAT_HISTORY_COSMOS_ENABLED),
                request.app.state.config.get(CONFIG_CHAT_HISTORY_BROWSER_ENABLED),
            )

        result_gen = await approach.run_stream(body["messages"], context=context, session_state=session_state)
        return StreamingResponse(ndjson_bytes(result_gen), media_type="application/x-ndjson")
    except Exception as error:
        return JSONResponse({"error": str(error)}, status_code=500)


@router.post("/chat")
async def chat(request: Request, auth_claims: dict = Depends(get_auth_claims)):
    if request.headers.get("content-type", "").find("application/json") == -1:
        return JSONResponse({"error": "request must be json"}, status_code=415)
    body = await request.json()
    context = body.get("context", {}) or {}
    context["auth_claims"] = auth_claims
    try:
        approach = request.app.state.config.get(CONFIG_CHAT_APPROACH)
        if approach is None:
            return JSONResponse({"error": "Chat approach not configured"}, status_code=503)

        session_state = body.get("session_state")
        if session_state is None:
            from core.sessionhelper import create_session_id

            session_state = create_session_id(
                request.app.state.config.get(CONFIG_CHAT_HISTORY_COSMOS_ENABLED),
                request.app.state.config.get(CONFIG_CHAT_HISTORY_BROWSER_ENABLED),
            )

        result = await approach.run(body["messages"], context=context, session_state=session_state)
        return JSONResponse(result)
    except Exception as error:
        return JSONResponse({"error": str(error)}, status_code=500)
