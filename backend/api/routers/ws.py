from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..ws import manager

router = APIRouter()


@router.websocket("/ws/graph-updates")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
