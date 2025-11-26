from __future__ import annotations

from fastapi import APIRouter

from ..config import SETTINGS

router = APIRouter()


@router.get("/api/admin/settings")
async def get_settings():
    return {"use_db": SETTINGS.use_db, "max_concurrent_runs": SETTINGS.max_concurrent_runs}
