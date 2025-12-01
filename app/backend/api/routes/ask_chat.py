"""Ask and chat endpoints (including NDJSON streaming) using Pydantic models and DI."""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse

from ..models import AskRequest, ChatRequest
from .utils import ndjson_bytes
from ..dependencies import get_auth_claims, get_ask_approach, get_chat_approach
from config import CONFIG_CHAT_HISTORY_BROWSER_ENABLED, CONFIG_CHAT_HISTORY_COSMOS_ENABLED

router = APIRouter()


@router.post("/ask")
async def ask(
    body: AskRequest,
    auth_claims: dict = Depends(get_auth_claims),
    approach=Depends(get_ask_approach),
):
    context = body.context or {}
    context["auth_claims"] = auth_claims
    try:
        r = await approach.run([m.dict() for m in body.messages], context=context, session_state=body.session_state)
        return JSONResponse(r)
    except Exception as error:
        return JSONResponse({"error": str(error)}, status_code=500)


@router.post("/chat/stream")
async def chat_stream(
    request: Request,
    body: ChatRequest,
    auth_claims: dict = Depends(get_auth_claims),
    approach=Depends(get_chat_approach),
):
    context = body.context or {}
    context["auth_claims"] = auth_claims
    try:
        session_state = body.session_state
        if session_state is None:
            from core.sessionhelper import create_session_id

            cfg = getattr(request.app.state, "config", {})
            session_state = create_session_id(
                cfg.get(CONFIG_CHAT_HISTORY_COSMOS_ENABLED),
                cfg.get(CONFIG_CHAT_HISTORY_BROWSER_ENABLED),
            )

        result_gen = await approach.run_stream([m.dict() for m in body.messages], context=context, session_state=session_state)
        return StreamingResponse(ndjson_bytes(result_gen), media_type="application/x-ndjson")
    except Exception as error:
        return JSONResponse({"error": str(error)}, status_code=500)


@router.post("/chat")
async def chat(
    request: Request,
    body: ChatRequest,
    auth_claims: dict = Depends(get_auth_claims),
    approach=Depends(get_chat_approach),
):
    context = body.context or {}
    context["auth_claims"] = auth_claims
    try:
        session_state = body.session_state
        if session_state is None:
            from core.sessionhelper import create_session_id

            cfg = getattr(request.app.state, "config", {})
            session_state = create_session_id(
                cfg.get(CONFIG_CHAT_HISTORY_COSMOS_ENABLED),
                cfg.get(CONFIG_CHAT_HISTORY_BROWSER_ENABLED),
            )

        result = await approach.run([m.dict() for m in body.messages], context=context, session_state=session_state)
        return JSONResponse(result)
    except Exception as error:
        return JSONResponse({"error": str(error)}, status_code=500)
