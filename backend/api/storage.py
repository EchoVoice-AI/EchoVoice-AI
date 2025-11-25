"""Simple storage helpers for segments and snapshots.

This module provides a small abstraction over file-backed storage and an
optional Postgres-backed implementation (via `backend.api.db`) when
`DATABASE_URL` is set in the environment. It also contains a lightweight
helper to extract node names from `src/agent/graph.py` as a default
for new projects.
"""

from __future__ import annotations

import datetime
import json
import re
from pathlib import Path
from typing import Dict, List

from .config import SETTINGS

BASE_DIR = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = BASE_DIR / "segments_snapshots"
GRAPH_PY = BASE_DIR.parent / "src" / "agent" / "graph.py"

# Use Postgres-backed storage when configured via `SETTINGS`
USE_DB = bool(SETTINGS.use_db)
_db = None
if USE_DB:
    try:
        from . import db as _db  # type: ignore
    except Exception:
        _db = None


def ensure_snapshot_dir() -> None:
    """Ensure the snapshot directory exists.

    Creates `backend/segments_snapshots/` if it does not already exist.
    """
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)


def load_segments() -> List[Dict]:
    """Load the list of segments from the configured storage backend.

    Returns a list of segment dictionaries. When a Postgres database is
    configured, this function will attempt to read from it and fall back
    to the file-backed store on error.
    """
    # When DB mode is requested we must have a working DB backend module
    # available. If the `db` module failed to import earlier (`_db is
    # None`) then surface a clear error rather than returning `None` so
    # the server fails loud and the operator can fix the environment.
    if USE_DB:
        if _db is None:
            raise RuntimeError(
                "DATABASE_URL is set but the DB backend module could not be imported. "
                "Ensure required DB dependencies (psycopg, sqlmodel) are installed and "
                "that the environment is configured correctly."
            )

        return _db.get_all_segments()


def save_segments(segments: List[Dict]) -> None:
    """Persist the list of segments to the configured backend.

    If a DB is configured this writes to the DB via `replace_all_segments`,

    """
    if USE_DB:
        if _db is None:
            raise RuntimeError(
                "DATABASE_URL is set but the DB backend module could not be imported. "
                "Ensure required DB dependencies (psycopg, sqlmodel) are installed and "
                "that the environment is configured correctly."
            )

        _db.replace_all_segments(segments)
        return


def snapshot_segments(segments: List[Dict], message: str | None = None) -> Path:
    """Write a timestamped snapshot of segments and return the path.

    The snapshot payload contains a `timestamp`, optional `message`, and the
    full `segments` payload so snapshots are self-describing.
    """
    ensure_snapshot_dir()
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    name = f"segments_snapshot_{ts}.json"
    path = SNAPSHOT_DIR / name
    payload = {"timestamp": ts, "message": message, "segments": segments}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return path


_ADD_NODE_RE = re.compile(r"\.add_node\(\s*[\"']([a-zA-Z0-9_]+)[\"']")


def default_segments_from_graph() -> List[Dict]:
    """Extract sensible default segment entries by scanning `graph.py`.

    This function scans `src/agent/graph.py` for `.add_node("name")` calls
    and returns a list of simple segment dicts for names that look like
    segmentation nodes. If the scan fails, a small default list is
    returned to bootstrap the editor UI.
    """
    nodes: List[str] = []
    try:
        text = GRAPH_PY.read_text(encoding="utf-8")
        nodes = _ADD_NODE_RE.findall(text)
    except Exception:
        nodes = [
            "profile_segmentor_node",
            "rfm_segmentor_node",
            "intent_segmentor_node",
            "behavioral_segmentor_node",
            "priority_node",
        ]
    segments: List[Dict] = []
    for n in nodes:
        if "segment" in n or "rfm" in n or "priority" in n:
            segments.append({
                "id": n,
                "name": n,
                "enabled": True,
                "priority": 1.0,
                "metadata": {},
            })
    if not segments:
        segments = [
            {
                "id": "default_segment",
                "name": "default_segment",
                "enabled": True,
                "priority": 1.0,
                "metadata": {},
            }
        ]
    return segments
