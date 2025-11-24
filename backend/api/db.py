"""Database helpers for Postgres-backed segment storage.

This module uses SQLModel to define a simple `SegmentModel` table and
provides convenience functions for creating tables and performing basic
CRUD operations. All functions raise a `RuntimeError` if `DATABASE_URL`
is not configured via the environment.
"""

from __future__ import annotations

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
