from __future__ import annotations

import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, List
import asyncio

from . import storage
from .schemas import Segment, SegmentUpdate, GraphSummary, ValidationResult

# Ensure src/ is importable if necessary
src_root = Path(__file__).resolve().parents[2] / "src"
if str(src_root) not in sys.path:
    sys.path.insert(0, str(src_root))

app = FastAPI(title="EchoVoice LangGraph API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        try:
            self.active_connections.remove(websocket)
        except ValueError:
            pass

    async def broadcast(self, message: Dict):
        living = []
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
                living.append(connection)
            except Exception:
                pass
        self.active_connections = living


manager = ConnectionManager()


@app.get("/api/graph", response_model=GraphSummary)
async def get_graph():
    # Build a lightweight summary by scanning graph.py for add_node calls.
    nodes = []
    try:
        nodes = storage.default_segments_from_graph()
        node_names = [s["name"] for s in nodes]
    except Exception:
        node_names = []
    return GraphSummary(name="EchoVoice Agent Graph", nodes=node_names)


@app.get("/api/segments", response_model=List[Segment])
async def list_segments():
    segments = storage.load_segments()
    return [Segment(**s) for s in segments]


@app.patch("/api/segments/{segment_id}", response_model=Segment)
async def update_segment(segment_id: str, payload: SegmentUpdate):
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
    storage.save_segments(segments)
    # broadcast update
    await manager.broadcast({"type": "segment.updated", "segment": found})
    return Segment(**found)


@app.post("/api/graph/validate", response_model=ValidationResult)
async def validate_graph():
    segments = storage.load_segments()
    errors = []
    if not any(s.get("enabled") for s in segments):
        errors.append("At least one segment must be enabled.")
    for s in segments:
        p = s.get("priority")
        if p is None or not (0.0 <= float(p) <= 1e6):
            errors.append(f"Segment {s.get('id')} has invalid priority: {p}")
    valid = len(errors) == 0
    return ValidationResult(valid=valid, errors=errors)


@app.post("/api/graph/commit")
async def commit_graph(message: str | None = None):
    segments = storage.load_segments()
    path = storage.snapshot_segments(segments, message=message)
    await manager.broadcast({"type": "graph.committed", "path": str(path)})
    return JSONResponse({"committed": True, "path": str(path)})


@app.websocket("/ws/graph-updates")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # keep connection open; consume messages if clients send any
            data = await websocket.receive_text()
            # echo or ignore
            await websocket.send_text(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
