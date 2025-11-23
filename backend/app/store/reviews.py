# backend/app/store/reviews.py

"""
Helpers for storing and retrieving HITL review objects.

A "review" represents a Human-in-the-Loop (HITL) review job created by HITLNode.
Reviews are stored in the shared app.store backend (MemoryStore or RedisStore)
under keys of the form:

    hitl:{review_id}

This module provides a small, typed API so other parts of the system
(HITLNode, HITL router, tests) can work with HITL reviews without
having to know the key format or storage details.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.store import store


def _review_key(review_id: str) -> str:
    """
    Build the storage key for a given review_id.

    Example:
        review_id = "abc123" -> "hitl:abc123"
    """
    return f"hitl:{review_id}"


def _now_iso() -> str:
    """
    Return current time as an ISO 8601 string in UTC.

    Using a string keeps the review object JSON-serializable, which is
    important for RedisStore where values are stored as JSON.
    """
    return datetime.now(timezone.utc).isoformat()


def create_review(
    review_id: str,
    customer: Dict[str, Any],
    variants: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Create and persist a new HITL review object.

    Args:
        review_id: Unique identifier for the review. Should be stable and
                   used to look up this review later via GET /hitl/{review_id}.
        customer:  Customer payload (dict) from the orchestrator / flow state.
        variants:  List of safe variants (dicts) produced by the generator/safety
                   pipeline. Each should include at least an "id" and "text" field.

    Returns:
        The full review object as stored.
    """
    now = _now_iso()
    review: Dict[str, Any] = {
        "review_id": review_id,
        "customer": customer,
        "variants": variants,
        "status": "pending_human_approval",
        "approved_variant_id": None,
        "notes": None,
        "created_at": now,
        "updated_at": now,
    }

    store.set(_review_key(review_id), review)
    return review


def get_review(review_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a HITL review by ID.

    Args:
        review_id: The review identifier used when it was created.

    Returns:
        The review dict if found, or None if not present in the store.
    """
    return store.get(_review_key(review_id))


def save_review(review: Dict[str, Any]) -> None:
    """
    Persist an updated HITL review object.

    This function:
    - Updates the `updated_at` timestamp.
    - Writes the review back to the underlying store.

    It assumes `review["review_id"]` is present.

    Args:
        review: The full review object to save.
    """
    review_id = review.get("review_id")
    if not review_id:
        raise ValueError("review object must contain a 'review_id' field")

    review["updated_at"] = _now_iso()
    store.set(_review_key(review_id), review)
