# backend/app/store/audit_log.py

"""
Audit logging for Human-in-the-Loop (HITL) interactions.

This module records a time-ordered list of actions for each review_id,
so we can answer questions like:
- Who approved which variant, and when?
- How often did the reviewer use TTS, STT, or Translate?
- What language / modality was used?

Logs are stored in the shared app.store backend (MemoryStore / RedisStore)
under keys of the form:

    hitl:log:{review_id}

Each log entry is a dict with:
    {
        "timestamp": ISO-8601 UTC string,
        "review_id": str | None,
        "user_id": str | None,
        "action": str,
        "metadata": dict
    }
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.store import store


def _log_key(review_id: str) -> str:
    """
    Build the storage key for logs belonging to a specific review_id.
    """
    return f"hitl:log:{review_id}"


def _now_iso() -> str:
    """
    Return current time as an ISO 8601 string in UTC.
    """
    return datetime.now(timezone.utc).isoformat()


def log_action(
    review_id: Optional[str],
    action: str,
    user_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Append a single audit log entry for a given review_id.

    Args:
        review_id: The HITL review ID this action is associated with.
                   Can be None if not tied to a specific review, but
                   grouping by review_id is recommended when available.
        action:    A short action code, e.g.:
                     - "TTS_PLAY"
                     - "STT_TRANSCRIBE"
                     - "TRANSLATE"
                     - "APPROVE_DECISION"
        user_id:   Identifier for the human reviewer or system user (if known).
        metadata:  Extra context (e.g. variant_id, target_lang, audio_url).
    """
    if review_id is None:
        # If there's no review_id, we currently skip logging.
        # You can extend this later to support global logs if needed.
        return

    key = _log_key(review_id)
    entry = {
        "timestamp": _now_iso(),
        "review_id": review_id,
        "user_id": user_id,
        "action": action,
        "metadata": metadata or {},
    }

    # Load existing log list (if any), append, and save back.
    logs: Optional[List[Dict[str, Any]]] = store.get(key)
    if logs is None:
        logs = []

    logs.append(entry)
    store.set(key, logs)


def get_logs(review_id: str) -> List[Dict[str, Any]]:
    """
    Fetch all audit log entries for a given review_id.

    Returns:
        A list of log entry dicts (possibly empty if nothing logged yet).
    """
    logs = store.get(_log_key(review_id))
    return logs or []
