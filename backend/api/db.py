"""Database helpers for Postgres-backed segment storage.

This module uses SQLModel to define a simple `SegmentModel` table and
provides convenience functions for creating tables and performing basic
CRUD operations. All functions raise a `RuntimeError` if `DATABASE_URL`
is not configured via the environment.
"""

from __future__ import annotations

import datetime
import logging
import os
from typing import List

from sqlalchemy import JSON as SA_JSON
from sqlalchemy import Column
from sqlalchemy import delete as sa_delete
from sqlmodel import Field, Session, SQLModel, create_engine, select

DATABASE_URL = os.environ.get("DATABASE_URL")


class SegmentModel(SQLModel, table=True):
    """SQLModel table for storing Segment objects.

    The model stores `id`, `name`, `enabled`, `priority`, and a JSON
    `metadata` column suitable for free-form metadata.
    """

    id: str = Field(primary_key=True)
    name: str
    enabled: bool = True
    priority: float = 1.0
    # Use a non-reserved attribute name for the JSON column to avoid
    # conflicts with SQLAlchemy/SQLModel's own `metadata` attribute.
    meta: dict = Field(default_factory=dict, sa_column=Column(SA_JSON))
    # Allow redefinition of the table within the same SQLAlchemy MetaData
    # instance (useful when the module is imported multiple times during
    # iterative development / REPL runs).
    __table_args__ = {"extend_existing": True}


# Create engine only if DATABASE_URL is provided
engine = None
if DATABASE_URL:
    # Use SQLModel/create_engine; note: psycopg (psycopg>=3) is required
    engine = create_engine(DATABASE_URL, echo=False)

# Logger for DB diagnostics
logger = logging.getLogger(__name__)


def create_db_and_tables() -> None:
    """Create database tables for models when a DB is configured.

    Raises:
        RuntimeError: if `DATABASE_URL` is not configured.
    """
    if engine is None:
        raise RuntimeError("DATABASE_URL not configured; cannot create tables")
    SQLModel.metadata.create_all(engine)


def get_all_segments() -> List[dict]:
    """Return all segments from the DB as a list of dictionaries.

    Raises:
        RuntimeError: if `DATABASE_URL` is not configured.
    """
    if engine is None:
        raise RuntimeError("DATABASE_URL not configured")
    with Session(engine) as session:
        rows = session.exec(select(SegmentModel)).all()
        results = []
        for r in rows:
            d = r.dict()
            # Map DB `meta` field back to `metadata` for API compatibility
            d["metadata"] = d.pop("meta", {})
            results.append(d)
        return results


def get_segment(segment_id: str) -> dict | None:
    """Fetch a single segment by `segment_id`.

    Returns None if not found.
    """
    if engine is None:
        raise RuntimeError("DATABASE_URL not configured")
    with Session(engine) as session:
        seg = session.get(SegmentModel, segment_id)
        if seg is None:
            return None
        d = seg.dict()
        d["metadata"] = d.pop("meta", {})
        return d


def upsert_segment(data: dict) -> dict:
    """Insert or update a single segment row and return it.

    This performs a simple read -> update/insert cycle using SQLModel's
    `Session`. It expects `data` to contain an `id` key.
    """
    if engine is None:
        raise RuntimeError("DATABASE_URL not configured")
    # Normalize input mapping: accept `metadata` key from callers and map
    # it to the DB model's `meta` attribute.
    payload = dict(data)
    if "metadata" in payload:
        payload["meta"] = payload.pop("metadata")
    seg = SegmentModel(**payload)
    with Session(engine) as session:
        existing = session.get(SegmentModel, seg.id)
        if existing:
            # update fields
            existing.name = seg.name
            existing.enabled = seg.enabled
            existing.priority = seg.priority
            existing.meta = seg.meta
            session.add(existing)
            session.commit()
            session.refresh(existing)
            d = existing.dict()
            d["metadata"] = d.pop("meta", {})
            return d
        else:
            session.add(seg)
            session.commit()
            session.refresh(seg)
            d = seg.dict()
            d["metadata"] = d.pop("meta", {})
            return d


def replace_all_segments(segments: List[dict]) -> None:
    """Replace all segments in the DB with the provided list.

    This function deletes all existing rows and inserts the provided
    segments. It's a simple approach suitable for small datasets.
    """
    if engine is None:
        raise RuntimeError("DATABASE_URL not configured")
    with Session(engine) as session:
        # Simple approach: delete all then insert
        session.exec(sa_delete(SegmentModel))
        session.commit()
        for s in segments:
            payload = dict(s)
            if "metadata" in payload:
                payload["meta"] = payload.pop("metadata")
            session.add(SegmentModel(**payload))
        session.commit()


class RunModel(SQLModel, table=True):
    """Persisted run metadata for async/sync executions.

    Stores the `payload` (the run input), `result`, `logs` as JSON and
    `status` to coordinate queued/running/finished runs.
    """

    id: str = Field(primary_key=True)
    status: str = Field(default="queued")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    payload: dict = Field(default_factory=dict, sa_column=Column(SA_JSON))
    result: dict = Field(default_factory=dict, sa_column=Column(SA_JSON))
    logs: list = Field(default_factory=list, sa_column=Column(SA_JSON))

    __table_args__ = {"extend_existing": True}


def create_run(run_id: str, payload: dict, status: str = "queued") -> None:
    """Create a persisted run record."""
    if engine is None:
        raise RuntimeError("DATABASE_URL not configured")
    with Session(engine) as session:
        r = RunModel(id=run_id, status=status, payload=payload)
        session.add(r)
        session.commit()


def update_run_status(run_id: str, status: str) -> None:
    """Update status for an existing run record."""
    if engine is None:
        raise RuntimeError("DATABASE_URL not configured")
    with Session(engine) as session:
        r = session.get(RunModel, run_id)
        if r is None:
            return
        r.status = status
        r.updated_at = datetime.datetime.utcnow()
        session.add(r)
        session.commit()


def append_run_log(run_id: str, log_item: dict) -> None:
    """Append a single log entry to a run's logs JSON array."""
    if engine is None:
        raise RuntimeError("DATABASE_URL not configured")
    with Session(engine) as session:
        r = session.get(RunModel, run_id)
        if r is None:
            return
        logs = r.logs or []
        logs.append(log_item)
        r.logs = logs
        r.updated_at = datetime.datetime.utcnow()
        session.add(r)
        session.commit()


def set_run_result(run_id: str, result: dict) -> None:
    """Set the final result JSON for a run and update timestamp."""
    if engine is None:
        raise RuntimeError("DATABASE_URL not configured")
    with Session(engine) as session:
        r = session.get(RunModel, run_id)
        if r is None:
            return
        r.result = result
        r.updated_at = datetime.datetime.utcnow()
        session.add(r)
        session.commit()


def get_run(run_id: str) -> dict | None:
    """Retrieve a persisted run record as a dict, or None if missing."""
    if engine is None:
        raise RuntimeError("DATABASE_URL not configured")
    with Session(engine) as session:
        r = session.get(RunModel, run_id)
        if r is None:
            return None
        d = r.dict()
        return d


def list_runs(status: str | None = None, limit: int = 100) -> List[dict]:
    """List persisted runs optionally filtered by status."""
    if engine is None:
        raise RuntimeError("DATABASE_URL not configured")
    with Session(engine) as session:
        q = select(RunModel)
        if status:
            q = q.where(RunModel.status == status)
        rows = session.exec(q).all()
        return [r.dict() for r in rows][:limit]


def count_active_runs() -> int:
    """Return count of runs currently in running/cancelling states."""
    if engine is None:
        raise RuntimeError("DATABASE_URL not configured")
    with Session(engine) as session:
        q = select(RunModel).where(RunModel.status.in_(["running", "cancelling"]))
        rows = session.exec(q).all()
        return len(rows)


def get_queued_runs(limit: int = 10) -> List[dict]:
    """Return queued runs ordered by creation time (oldest first)."""
    if engine is None:
        raise RuntimeError("DATABASE_URL not configured")
    with Session(engine) as session:
        q = select(RunModel).where(RunModel.status == "queued").order_by(RunModel.created_at)
        rows = session.exec(q).all()
        return [r.dict() for r in rows][:limit]
