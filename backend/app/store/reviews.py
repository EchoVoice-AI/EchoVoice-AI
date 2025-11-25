# backend/app/store/reviews.py

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.store.memory_store import MemoryStore  # or your actual store class

_STORE_KEY_PREFIX = "hitl:review:"

store = MemoryStore()  # or whatever you’re already using


def _key(review_id: str) -> str:
    return f"{_STORE_KEY_PREFIX}{review_id}"


def create_review(
    review_id: str,
    customer: Dict[str, Any],
    variants: list[Dict[str, Any]],
) -> Dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()

    review = {
        "review_id": review_id,
        "customer": customer,
        "variants": variants,
        "status": "pending_human_approval",
        "approved_variant_id": None,
        "notes": None,
        "created_at": now,
        "updated_at": now,
    }

    store.set(_key(review_id), review)
    return review


def get_review(review_id: str) -> Optional[Dict[str, Any]]:
    return store.get(_key(review_id))


def update_review(
    review_id: str,
    *,
    status: Optional[str] = None,
    approved_variant_id: Optional[str] = None,
    notes: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Update an existing HITL review.

    Only fields passed (not None) are updated. Returns the updated review,
    or None if the review does not exist.
    """
    review = get_review(review_id)
    if review is None:
        return None

    changed = False

    if status is not None:
        review["status"] = status
        changed = True

    if approved_variant_id is not None:
        review["approved_variant_id"] = approved_variant_id
        changed = True

    if notes is not None:
        review["notes"] = notes
        changed = True

    if changed:
        review["updated_at"] = datetime.now(timezone.utc).isoformat()
        store.set(_key(review_id), review)

    return review
