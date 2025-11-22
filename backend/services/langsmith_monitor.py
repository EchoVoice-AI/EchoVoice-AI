"""Opt-in LangSmith monitor wrapper.

This module provides a tiny, safe API to record agent runs/events.
By default it is a no-op. To enable real recording set the env var
`LANGSMITH_API_KEY` (or `LANGSMITH_ENABLED=1`). If the `langsmith`
SDK is not installed but the wrapper is enabled, it will write
local JSON files under `backend/.langsmith_local_runs/` for inspection.

The API is intentionally small and synchronous to keep it low-risk.
"""
from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_ENABLED = bool(os.getenv("LANGSMITH_ENABLED") == "1" or LANGSMITH_API_KEY)

# Try to import the real langsmith SDK if available. We don't require it.
HAS_SDK = False
_client = None
try:
    import langsmith

    HAS_SDK = True
    # Defer client creation until needed and after validating API key
except Exception:
    HAS_SDK = False


RUNS_DIR = Path(__file__).resolve().parents[1] / ".langsmith_local_runs"
RUNS_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> float:
    return time.time()


def start_run(name: str, metadata: Optional[Dict[str, Any]] = None) -> str:
    """Start a run and return a run_id.

    This is lightweight and synchronous. If disabled, returns a generated id
    but does not persist anything.
    """
    run_id = str(uuid.uuid4())
    metadata = metadata or {}
    record = {
        "id": run_id,
        "name": name,
        "metadata": metadata,
        "start_time": _now(),
        "events": [],
    }

    if not LANGSMITH_ENABLED:
        return run_id

    if HAS_SDK and LANGSMITH_API_KEY:
        # If the LangSmith client API is available, integrate here.
        # We avoid a hard dependency on the SDK; implement direct client
        # wiring later if desired. For now, write a local file as well.
        pass

    # Write initial record to local file for visibility
    path = RUNS_DIR / f"{run_id}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)

    return run_id


def log_event(run_id: str, name: str, payload: Optional[Dict[str, Any]] = None) -> None:
    """Log a named event to the run record. No-op if disabled."""
    if not LANGSMITH_ENABLED:
        return

    payload = payload or {}
    path = RUNS_DIR / f"{run_id}.json"
    if not path.exists():
        # Create a minimal record if missing
        rec = {
            "id": run_id,
            "name": None,
            "metadata": {},
            "start_time": _now(),
            "events": [],
        }
    else:
        with path.open("r", encoding="utf-8") as f:
            try:
                rec = json.load(f)
            except Exception:
                rec = {"id": run_id, "events": []}

    rec.setdefault("events", []).append({"time": _now(), "name": name, "payload": payload})

    with path.open("w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)


def finish_run(run_id: str, status: str = "success", outputs: Optional[Dict[str, Any]] = None) -> None:
    """Finish the run by marking end time and optional outputs. No-op if disabled."""
    if not LANGSMITH_ENABLED:
        return

    outputs = outputs or {}
    path = RUNS_DIR / f"{run_id}.json"
    if not path.exists():
        rec = {"id": run_id, "events": []}
    else:
        with path.open("r", encoding="utf-8") as f:
            try:
                rec = json.load(f)
            except Exception:
                rec = {"id": run_id, "events": []}

    rec["end_time"] = _now()
    rec["status"] = status
    rec["outputs"] = outputs

    with path.open("w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)


__all__ = ["start_run", "log_event", "finish_run", "LANGSMITH_ENABLED"]
