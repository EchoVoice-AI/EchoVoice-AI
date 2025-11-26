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
GRAPH_CONFIG_PATH = BASE_DIR / "data" / "graph_config.json"

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


def load_graph_config() -> Dict:
    """Load a lightweight graph configuration JSON used by the frontend editor.

    The config is intentionally minimal: `name`, `nodes`, and `edges` so the
    frontend can edit a simple representation without touching Python source.
    If no config exists, a default structure is returned.
    """
    if GRAPH_CONFIG_PATH.exists():
        try:
            with open(GRAPH_CONFIG_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # Fallback default built from node names
    nodes = default_segments_from_graph()
    node_objs = [
        {"id": s["id"], "label": s["name"], "type": "segment", "metadata": s.get("metadata", {})}
        for s in nodes
    ]
    # A very small default set of edges mirroring `src/agent/graph.py` composition
    edges = [
        {"from": "START", "to": "rfm_segmentor_node"},
        {"from": "START", "to": "intent_segmentor_node"},
        {"from": "START", "to": "behavioral_segmentor_node"},
        {"from": "START", "to": "profile_segmentor_node"},
    ]
    return {"name": "EchoVoice Agent Graph", "nodes": node_objs, "edges": edges}


def save_graph_config(cfg: Dict) -> None:
    """Persist the simple graph configuration to disk.

    Overwrites the JSON file at `GRAPH_CONFIG_PATH`.
    """
    try:
        with open(GRAPH_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception:
        # Best-effort: raise to let caller return 500
        raise


def upload_blob(data: bytes, blob_name: str, content_type: str | None = None) -> str:
    """Upload raw bytes to Azure Blob Storage and return the blob URL.

    Requires `SETTINGS.azure_storage_connection_string` to be set. This
    is a thin helper around `azure.storage.blob.BlobServiceClient`.
    """
    conn_str = getattr(SETTINGS, "azure_storage_connection_string", None)
    container = getattr(SETTINGS, "azure_storage_container", "echovoice-uploads")
    if not conn_str:
        raise RuntimeError("AZURE_STORAGE_CONNECTION_STRING is not configured")

    try:
        from azure.storage.blob import BlobServiceClient
        try:
            # ContentSettings is optional and may be absent in some shim packages
            from azure.storage.blob import ContentSettings  # type: ignore
        except Exception:
            ContentSettings = None
    except Exception as exc:  # pragma: no cover - runtime dependency
        raise RuntimeError("azure.storage.blob package is required for blob uploads") from exc

    svc = BlobServiceClient.from_connection_string(conn_str)
    container_client = svc.get_container_client(container)
    try:
        container_client.create_container()
    except Exception:
        # ignore if already exists or creation fails due to permissions
        pass

    blob_client = container_client.get_blob_client(blob_name)
    content_settings = None
    if ContentSettings is not None and content_type:
        content_settings = ContentSettings(content_type=content_type)

    blob_client.upload_blob(data, overwrite=True, content_settings=content_settings)
    return blob_client.url


def upload_fileobj(fileobj, blob_name: str, content_type: str | None = None) -> str:
    """Upload a file-like object (has .read()) to Azure Blob Storage."""
    # Default implementation: stream the file-like object to Azure without
    # buffering the entire content in memory. Ensure fileobj is seeked to
    # the beginning when possible.
    try:
        fileobj.seek(0)
    except Exception:
        pass
    return upload_fileobj_stream(fileobj, blob_name, content_type=content_type)


def upload_fileobj_stream(fileobj, blob_name: str, content_type: str | None = None) -> str:
    """Stream a file-like object directly to Azure Blob Storage.

    This does not read the entire file into memory and is suitable for
    large uploads. `fileobj` should be a file-like object opened in binary
    mode (e.g., UploadFile.file from FastAPI).
    """
    conn_str = getattr(SETTINGS, "azure_storage_connection_string", None)
    container = getattr(SETTINGS, "azure_storage_container", "echovoice-uploads")
    if not conn_str:
        raise RuntimeError("AZURE_STORAGE_CONNECTION_STRING is not configured")

    try:
        from azure.storage.blob import BlobServiceClient
        try:
            from azure.storage.blob import ContentSettings  # type: ignore
        except Exception:
            ContentSettings = None
    except Exception as exc:  # pragma: no cover - runtime dependency
        raise RuntimeError("azure.storage.blob package is required for blob uploads") from exc

    svc = BlobServiceClient.from_connection_string(conn_str)
    container_client = svc.get_container_client(container)
    try:
        container_client.create_container()
    except Exception:
        pass

    blob_client = container_client.get_blob_client(blob_name)
    content_settings = None
    if ContentSettings is not None and content_type:
        content_settings = ContentSettings(content_type=content_type)

    # azure SDK accepts a file-like object for upload_blob; use overwrite
    # to allow re-uploads with same name.
    blob_client.upload_blob(fileobj, overwrite=True, content_settings=content_settings)
    return blob_client.url
