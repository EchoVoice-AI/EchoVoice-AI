"""Aggregate API sub-routers for the application.

This module exposes a single `router` that includes graph, segments,
websocket, admin and blob-upload sub-routers. Importing `api.routes`
keeps the top-level application import stable.
"""

from __future__ import annotations

from fastapi import APIRouter

from . import admin, blob, graph, segments, ws

router = APIRouter()

# Include sub-routers (they define full paths like /api/graph/...)
router.include_router(graph.router)
router.include_router(segments.router)
router.include_router(ws.router)
router.include_router(admin.router)
router.include_router(blob.router)
