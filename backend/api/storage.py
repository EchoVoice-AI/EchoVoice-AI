from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List
import datetime
import re

BASE_DIR = Path(__file__).resolve().parents[1]
SEGMENTS_PATH = BASE_DIR / "segments.json"
SNAPSHOT_DIR = BASE_DIR / "segments_snapshots"
GRAPH_PY = BASE_DIR.parent / "src" / "agent" / "graph.py"


def ensure_snapshot_dir() -> None:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)


def load_segments() -> List[Dict]:
    if not SEGMENTS_PATH.exists():
        segments = default_segments_from_graph()
        save_segments(segments)
        return segments
    with open(SEGMENTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_segments(segments: List[Dict]) -> None:
    SEGMENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SEGMENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(segments, f, indent=2, ensure_ascii=False)


def snapshot_segments(segments: List[Dict], message: str | None = None) -> Path:
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
    # Try to extract node names from the graph.py source as a fallback
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
    segments = []
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
            {"id": "default_segment", "name": "default_segment", "enabled": True, "priority": 1.0, "metadata": {} }
        ]
    return segments
