"""Chat history endpoints backed by Cosmos (optional)."""
import time
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, Response

from config import (
    CONFIG_CHAT_HISTORY_COSMOS_ENABLED,
    CONFIG_COSMOS_HISTORY_CLIENT,
    CONFIG_COSMOS_HISTORY_CONTAINER,
    CONFIG_COSMOS_HISTORY_VERSION,
    CONFIG_CREDENTIAL,
)
from ..dependencies import get_auth_claims

router = APIRouter()


@router.post("/chat_history",tags=["ChatHistory"])
async def post_chat_history(request: Request, auth_claims: dict = Depends(get_auth_claims)):
    cfg = getattr(request.app.state, "config", None)
    if cfg is None:
        raise HTTPException(status_code=503, detail="App not initialized")

    if not cfg.get(CONFIG_CHAT_HISTORY_COSMOS_ENABLED):
        return JSONResponse({"error": "Chat history not enabled"}, status_code=400)

    container = cfg.get(CONFIG_COSMOS_HISTORY_CONTAINER)
    if not container:
        return JSONResponse({"error": "Chat history not enabled"}, status_code=400)

    entra_oid = auth_claims.get("oid")
    if not entra_oid:
        return JSONResponse({"error": "User OID not found"}, status_code=401)

    try:
        request_json = await request.json()
        session_id = request_json.get("id")
        message_pairs = request_json.get("answers")
        first_question = message_pairs[0][0]
        title = first_question + "..." if len(first_question) > 50 else first_question
        timestamp = int(time.time() * 1000)

        session_item = {
            "id": session_id,
            "version": cfg.get(CONFIG_COSMOS_HISTORY_VERSION),
            "session_id": session_id,
            "entra_oid": entra_oid,
            "type": "session",
            "title": title,
            "timestamp": timestamp,
        }

        message_pair_items = []
        for ind, message_pair in enumerate(message_pairs):
            message_pair_items.append(
                {
                    "id": f"{session_id}-{ind}",
                    "version": cfg.get(CONFIG_COSMOS_HISTORY_VERSION),
                    "session_id": session_id,
                    "entra_oid": entra_oid,
                    "type": "message_pair",
                    "question": message_pair[0],
                    "response": message_pair[1],
                }
            )

        batch_operations = [("upsert", (session_item,))] + [
            ("upsert", (message_pair_item,)) for message_pair_item in message_pair_items
        ]
        await container.execute_item_batch(batch_operations=batch_operations, partition_key=[entra_oid, session_id])
        return JSONResponse({}, status_code=201)
    except Exception as error:
        return JSONResponse({"error": str(error)}, status_code=500)


@router.get("/chat_history/sessions",tags=["ChatHistory"])
async def get_chat_history_sessions(request: Request, auth_claims: dict = Depends(get_auth_claims)):
    cfg = getattr(request.app.state, "config", None)
    if cfg is None:
        raise HTTPException(status_code=503, detail="App not initialized")
    if not cfg.get(CONFIG_CHAT_HISTORY_COSMOS_ENABLED):
        return JSONResponse({"error": "Chat history not enabled"}, status_code=400)
    container = cfg.get(CONFIG_COSMOS_HISTORY_CONTAINER)
    if not container:
        return JSONResponse({"error": "Chat history not enabled"}, status_code=400)
    entra_oid = auth_claims.get("oid")
    if not entra_oid:
        return JSONResponse({"error": "User OID not found"}, status_code=401)

    try:
        count = int(request.query_params.get("count", 10))
        continuation_token = request.query_params.get("continuation_token")

        res = container.query_items(
            query="SELECT c.id, c.entra_oid, c.title, c.timestamp FROM c WHERE c.entra_oid = @entra_oid AND c.type = @type ORDER BY c.timestamp DESC",
            parameters=[dict(name="@entra_oid", value=entra_oid), dict(name="@type", value="session")],
            partition_key=[entra_oid],
            max_item_count=count,
        )

        pager = res.by_page(continuation_token)
        sessions = []
        try:
            page = await pager.__anext__()
            continuation_token = pager.continuation_token  # type: ignore
            async for item in page:
                sessions.append({
                    "id": item.get("id"),
                    "entra_oid": item.get("entra_oid"),
                    "title": item.get("title", "untitled"),
                    "timestamp": item.get("timestamp"),
                })
        except StopAsyncIteration:
            continuation_token = None

        return JSONResponse({"sessions": sessions, "continuation_token": continuation_token})
    except Exception as error:
        return JSONResponse({"error": str(error)}, status_code=500)


@router.get("/chat_history/sessions/{session_id}",tags=["ChatHistory"])
async def get_chat_history_session(request: Request, session_id: str, auth_claims: dict = Depends(get_auth_claims)):
    cfg = getattr(request.app.state, "config", None)
    if cfg is None:
        raise HTTPException(status_code=503, detail="App not initialized")
    if not cfg.get(CONFIG_CHAT_HISTORY_COSMOS_ENABLED):
        return JSONResponse({"error": "Chat history not enabled"}, status_code=400)
    container = cfg.get(CONFIG_COSMOS_HISTORY_CONTAINER)
    if not container:
        return JSONResponse({"error": "Chat history not enabled"}, status_code=400)
    entra_oid = auth_claims.get("oid")
    if not entra_oid:
        return JSONResponse({"error": "User OID not found"}, status_code=401)

    try:
        res = container.query_items(
            query="SELECT * FROM c WHERE c.session_id = @session_id AND c.type = @type",
            parameters=[dict(name="@session_id", value=session_id), dict(name="@type", value="message_pair")],
            partition_key=[entra_oid, session_id],
        )

        message_pairs = []
        async for page in res.by_page():
            async for item in page:
                message_pairs.append([item["question"], item["response"]])

        return JSONResponse({"id": session_id, "entra_oid": entra_oid, "answers": message_pairs})
    except Exception as error:
        return JSONResponse({"error": str(error)}, status_code=500)


@router.delete("/chat_history/sessions/{session_id}",tags=["ChatHistory"])
async def delete_chat_history_session(request: Request, session_id: str, auth_claims: dict = Depends(get_auth_claims)):
    cfg = getattr(request.app.state, "config", None)
    if cfg is None:
        raise HTTPException(status_code=503, detail="App not initialized")
    if not cfg.get(CONFIG_CHAT_HISTORY_COSMOS_ENABLED):
        return JSONResponse({"error": "Chat history not enabled"}, status_code=400)
    container = cfg.get(CONFIG_COSMOS_HISTORY_CONTAINER)
    if not container:
        return JSONResponse({"error": "Chat history not enabled"}, status_code=400)
    entra_oid = auth_claims.get("oid")
    if not entra_oid:
        return JSONResponse({"error": "User OID not found"}, status_code=401)

    try:
        res = container.query_items(
            query="SELECT c.id FROM c WHERE c.session_id = @session_id",
            parameters=[dict(name="@session_id", value=session_id)],
            partition_key=[entra_oid, session_id],
        )

        ids_to_delete = []
        async for page in res.by_page():
            async for item in page:
                ids_to_delete.append(item["id"])

        batch_operations = [("delete", (id,)) for id in ids_to_delete]
        await container.execute_item_batch(batch_operations=batch_operations, partition_key=[entra_oid, session_id])
        return Response(status_code=204)
    except Exception as error:
        return JSONResponse({"error": str(error)}, status_code=500)
