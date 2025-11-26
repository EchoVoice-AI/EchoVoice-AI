"""Small admin routes used by the frontend for diagnostics and settings.

Exposes a minimal `/api/admin/settings` endpoint used by the UI.
"""

from __future__ import annotations

from fastapi import APIRouter

from ..config import SETTINGS

router = APIRouter()


@router.get("/api/admin/settings")
async def get_settings():
    """Return a small admin settings summary used by the frontend."""
    return {"use_db": SETTINGS.use_db, "max_concurrent_runs": SETTINGS.max_concurrent_runs}
