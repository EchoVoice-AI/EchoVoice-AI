from __future__ import annotations

from fastapi import APIRouter

from . import graph, segments, ws, admin

router = APIRouter()

# Include sub-routers (they define full paths like /api/graph/...)
router.include_router(graph.router)
router.include_router(segments.router)
router.include_router(ws.router)
router.include_router(admin.router)
