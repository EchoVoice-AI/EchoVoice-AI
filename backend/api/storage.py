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
import os
import re
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parents[1]
SEGMENTS_PATH = BASE_DIR / "segments.json"
SNAPSHOT_DIR = BASE_DIR / "segments_snapshots"
GRAPH_PY = BASE_DIR.parent / "src" / "agent" / "graph.py"

# Use Postgres-backed storage when DATABASE_URL is provided in environment
USE_DB = bool(os.environ.get("DATABASE_URL"))
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
    # Prefer DB when configured
    if USE_DB and _db is not None:
        try:
            return _db.get_all_segments()
        except Exception:
            # Fall back to file-based if DB read fails
            pass

    if not SEGMENTS_PATH.exists():
        segments = default_segments_from_graph()
        save_segments(segments)
        return segments
    with open(SEGMENTS_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_segments(segments: List[Dict]) -> None:
    """Persist the list of segments to the configured backend.

    If a DB is configured this writes to the DB via `replace_all_segments`,
    otherwise it writes a JSON file to `backend/segments.json`.
    """
    # Prefer DB when configured
    if USE_DB and _db is not None:
        try:
            _db.replace_all_segments(segments)
            return
        except Exception:
            # fall back to file if DB write fails
            pass

    SEGMENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SEGMENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(segments, f, indent=2, ensure_ascii=False)


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
