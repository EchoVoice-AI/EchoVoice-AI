"""Endpoints for listing and updating segments used by the graph editor.

These routes return segment metadata consumed by the frontend and allow
patch updates to toggle enablement, priority, or metadata.
"""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from .. import storage
from ..schemas import Segment, SegmentUpdate

router = APIRouter()


@router.get("/api/segments", response_model=List[Segment])
async def list_segments() -> List[Segment]:
    """Return the list of configured segments.

    Each segment is converted to the `Segment` response model.
    """
    segments = storage.load_segments()
    return [Segment(**s) for s in segments]


@router.patch("/api/segments/{segment_id}", response_model=Segment)
async def update_segment(segment_id: str, payload: SegmentUpdate) -> Segment:
    """Patch update a single segment by `segment_id` and persist the change."""
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

    try:
        if getattr(storage, "USE_DB", False) and getattr(storage, "_db", None) is not None:
            storage._db.upsert_segment(found)
        else:
            storage.save_segments(segments)
    except Exception:
        storage.save_segments(segments)

    # broadcast update happens in original routes via manager; keep simple here
    return Segment(**found)
