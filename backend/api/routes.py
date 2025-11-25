"""HTTP and WebSocket routes for the EchoVoice LangGraph API.

This module defines the REST endpoints for managing the segmentation
configuration and provides the WebSocket endpoint for live updates.
The router is intentionally small and delegates storage to `storage.py`.
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from . import runner, storage
from .schemas import GraphSummary, Segment, SegmentUpdate, ValidationResult
from .ws import manager

router = APIRouter()


@router.get("/api/graph", response_model=GraphSummary)
async def get_graph() -> GraphSummary:
    """Return a small summary of the composed agent graph.

    The implementation scans `src/agent/graph.py` to extract node names
    as a lightweight representation for the frontend.
    """
    nodes = []
    try:
        nodes = storage.default_segments_from_graph()
        node_names = [s["name"] for s in nodes]
    except Exception:
        node_names = []
    return GraphSummary(name="EchoVoice Agent Graph", nodes=node_names)

@router.get("/api/graph/config")
async def get_graph_config() -> Dict[str, Any]:
    """Return a lightweight, editable graph configuration used by the frontend."""
    cfg = storage.load_graph_config()
    return cfg

@router.put("/api/graph/config")
async def put_graph_config(payload: Dict[str, Any]):
    """Persist a lightweight graph configuration (file-backed)."""
    # Basic sanity: ensure keys exist
    if not isinstance(payload, dict) or "nodes" not in payload or "edges" not in payload:
        raise HTTPException(status_code=400, detail="Invalid graph config payload")
    try:
        storage.save_graph_config(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    # Broadcast a config update so connected clients may refresh
    await manager.broadcast({"type": "graph.config.updated", "config": payload})
    return JSONResponse({"saved": True})

@router.post("/api/graph/execute")
async def execute_graph(request: Dict[str, Any]):
    """Execute the pipeline against a provided `GraphState`-like payload.

    Request shape: { "run_request": { ...graph state... }, "async": true|false }
    """
    run_req = request.get("run_request") if isinstance(request, dict) else None
    if run_req is None:
        raise HTTPException(status_code=400, detail="Missing 'run_request' payload")
    async_mode = bool(request.get("async", True)) if isinstance(request, dict) else True

    run_id = str(uuid.uuid4())
    # initialize run in runner
    runner._init_run(run_id, run_req)

    if async_mode:
        # schedule background run and return run_id
        asyncio.create_task(runner.run_graph(run_req, run_id=run_id))
        return JSONResponse({"run_id": run_id, "status": "queued"})
    else:
        # run synchronously and return full result
        result = await runner.run_graph(run_req, run_id=run_id)
        return JSONResponse({"run_id": run_id, "status": "finished", "result": result})

@router.get("/api/graph/execute/{run_id}/status")
async def get_execute_status(run_id: str):
    s = runner.get_run_status(run_id)
    if s is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return s

@router.get("/api/graph/execute/{run_id}/logs")
async def get_execute_logs(run_id: str):
    s = runner.get_run_status(run_id)
    if s is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return {"logs": s.get("logs", [])}


@router.get("/api/segments", response_model=List[Segment])
async def list_segments() -> List[Segment]:
    """Return the current list of configured segments.

    When a database is configured, storage will read from the DB;
    """
    segments = storage.load_segments()
    return [Segment(**s) for s in segments]


@router.patch("/api/segments/{segment_id}", response_model=Segment)
async def update_segment(segment_id: str, payload: SegmentUpdate) -> Segment:
    """Apply a partial update to a segment and persist the change.

    This endpoint updates `enabled`, `priority`, or `metadata` fields.
    It broadcasts a `segment.updated` event via the WebSocket manager.
    """
    segments = storage.load_segments()
    found = None
    for s in segments:
        if s.get("id") == segment_id:
            found = s
            break
    if not found:
        raise HTTPException(status_code=404, detail="Segment not found")
    if payload.enabled is not None:
        found["enabled"] = payload.enabled
    if payload.priority is not None:
        found["priority"] = float(payload.priority)
    if payload.metadata is not None:
        found["metadata"] = payload.metadata

    # Persist the change (DB preferred when configured)
    try:
        if getattr(storage, "USE_DB", False) and getattr(storage, "_db", None) is not None:
            storage._db.upsert_segment(found)
        else:
            storage.save_segments(segments)
    except Exception:
        # best-effort fallback to file storage
        storage.save_segments(segments)

    # broadcast update to connected clients
    await manager.broadcast({"type": "segment.updated", "segment": found})
    return Segment(**found)


@router.post("/api/graph/validate", response_model=ValidationResult)
async def validate_graph() -> ValidationResult:
    """Run lightweight validation on the current graph configuration.

    Example checks include ensuring at least one segment is enabled and
    priorities are numeric within a sane range.
    """
    segments = storage.load_segments()
    errors: List[str] = []
    if not any(s.get("enabled") for s in segments):
        errors.append("At least one segment must be enabled.")
    for s in segments:
        p = s.get("priority")
        try:
            pv = float(p)
            if not (0.0 <= pv <= 1e6):
                errors.append(f"Segment {s.get('id')} has invalid priority: {p}")
        except Exception:
            errors.append(f"Segment {s.get('id')} has non-numeric priority: {p}")
    valid = len(errors) == 0
    return ValidationResult(valid=valid, errors=errors)


@router.post("/api/graph/commit")
async def commit_graph(message: str | None = None):
    """Persist a snapshot of the current segments configuration.

    The snapshot is written to `backend/segments_snapshots/` (file) and a
    `graph.committed` event is broadcast to WebSocket clients.
    """
    segments = storage.load_segments()
    path = storage.snapshot_segments(segments, message=message)
    await manager.broadcast({"type": "graph.committed", "path": str(path)})
    return JSONResponse({"committed": True, "path": str(path)})


@router.websocket("/ws/graph-updates")
async def websocket_endpoint(websocket: WebSocket):
    """Accept WebSocket connections for graph update broadcasts.

    The server keeps a simple echo loop so clients may send messages, but
    the primary purpose is to receive broadcast events from other API
    operations.
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back whatever the client sent to keep client happy.
            await websocket.send_text(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
