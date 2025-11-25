# backend/app/routers/hitl.py

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.store import reviews as review_store
from app.store import audit_log

# This must be named `router` so `from app.routers.hitl import router` works
router = APIRouter(
    prefix="/hitl",
    tags=["hitl"],
)


# ---------- Pydantic models ---------- #

class HITLDecisionRequest(BaseModel):
    """Request body for human decision on a HITL review."""
    approved_variant_id: str
    notes: Optional[str] = None


# ---------- Endpoints ---------- #

@router.get("/{review_id}")
async def get_hitl_review(review_id: str):
    """
    Fetch a HITL review by ID.

    Returns the full review as stored in the review store.
    """
    review = review_store.get_review(review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.post("/{review_id}/decision")
async def submit_hitl_decision(review_id: str, payload: HITLDecisionRequest):
    """
    Submit a human decision for a HITL review.

    - Marks the review as 'approved'
    - Stores approved_variant_id and optional notes
    - Writes an audit log entry
    """
    review = review_store.get_review(review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")

    updated = review_store.update_review(
        review_id=review_id,
        status="approved",
        approved_variant_id=payload.approved_variant_id,
        notes=payload.notes,
    )

    audit_log.log_action(
        review_id=review_id,
        user_id=None,  # TODO: plug in real reviewer ID once auth is wired
        action="DECISION_SUBMIT",
        metadata={
            "approved_variant_id": payload.approved_variant_id,
            "notes_present": bool(payload.notes),
        },
    )

    return updated
