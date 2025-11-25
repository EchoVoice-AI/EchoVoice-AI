
"""Main entrypoint for ASGI servers.

This module exposes the application instance `app` created in
`.app.create_app()` so that Uvicorn/Gunicorn can import `api.main:app`.

We attach a startup event which validates DB connectivity when
`DATABASE_URL` is set so failures are logged early and clearly.
"""

from __future__ import annotations

import logging

from sqlalchemy import text

from .app import app
from .config import SETTINGS

logger = logging.getLogger(__name__)


@app.on_event("startup")
def check_database_connection() -> None:
    """Validate DB connectivity on startup when `SETTINGS.use_db` is true.

    This performs a small, lightweight query through the SQLModel
    `Session` to ensure the database is reachable. Any error is logged
    with traceback and re-raised so the process fails loudly.
    """
    if not SETTINGS.use_db:
        logger.info("DATABASE_URL not set — running in file-backed storage mode.")
        return

    try:
        # Import here to avoid import-time side-effects when DB is not used
        from . import db as _db  # type: ignore

        engine = getattr(_db, "engine", None)
        if engine is None:
            raise RuntimeError("DB engine is not initialized (engine is None)")

        # Run a trivial lightweight check: open a session and attempt a simple select
        from sqlmodel import Session

        try:
            with Session(engine) as session:  # type: ignore[arg-type]
                session.exec(text("SELECT 1"))
        except Exception as exc:  # pragma: no cover - runtime check
            raise RuntimeError(f"Failed to run test query against DB: {exc}") from exc

        logger.info("Database connectivity verified for %s", SETTINGS.DATABASE_URL)
    except Exception as exc:  # pragma: no cover - surface startup issues
        logger.exception("Database startup check failed: %s", exc)
        # Re-raise to fail startup loudly
        raise

