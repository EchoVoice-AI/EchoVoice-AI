"""WebSocket utilities and connection manager for API broadcasts.

This module provides a simple ConnectionManager used by API routes
to broadcast JSON messages to connected WebSocket clients.
"""

from __future__ import annotations

from typing import Dict, List

from fastapi import WebSocket


class ConnectionManager:
    """Manage active WebSocket connections and broadcasting.

    Methods are small and intentionally simple: connect, disconnect, and
    broadcast JSON-compatible messages to all active clients.
    """

    def __init__(self) -> None:
        """Initialize the connection manager with an empty connection list."""
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Accept and register a new WebSocket connection.

        Args:
            websocket: The FastAPI `WebSocket` instance to accept.
        """
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket from the active connections list.

        This method ignores the request if the websocket is not present.
        """
        try:
            self.active_connections.remove(websocket)
        except ValueError:
            pass

    async def broadcast(self, message: Dict) -> None:
        """Send a JSON-serializable `message` to all active clients.

        The connection list is pruned of clients that raise errors during
        send to keep the manager healthy.
        """
        living: List[WebSocket] = []
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
                living.append(connection)
            except Exception:
                # drop the broken connection
                pass
        self.active_connections = living


# Create a module-level manager instance that routes can import.
manager = ConnectionManager()
