"""WebSocket router that provides a lightweight relay endpoint for graph updates.

Clients can connect to `/ws/graph-updates` to receive broadcast messages
emitted by the runner or other administrative actions.
"""

from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..ws import manager

router = APIRouter()


@router.websocket("/ws/graph-updates")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint that relays graph update messages to connected clients."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
