"""Application factory and ASGI `app` for the EchoVoice API.

This module creates the FastAPI application, configures CORS, and
includes the route definitions from `routes.py`.
"""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from sqlalchemy import text

# Attempt to load backend/.env automatically (best-effort) so developers
# can set `DATABASE_URL` there without having to export it in the shell.
try:
    from dotenv import load_dotenv

    backend_root = Path(__file__).resolve().parents[1]
    dotenv_path = backend_root / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path=str(dotenv_path))
        logging.getLogger(__name__).info("Loaded environment from %s", dotenv_path)
    else:
        logging.getLogger(__name__).info("No .env file at %s; proceeding without loading .env", dotenv_path)
except Exception:
    # If python-dotenv is not installed, continue — require env vars be set externally.
    logging.getLogger(__name__).info("python-dotenv not available; ensure DATABASE_URL is set in the environment if using DB mode")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import storage
from .config import SETTINGS
from .routes import router as api_router

_ = SETTINGS

# Quick import-time diagnostic to show DB mode and whether DB backend loaded.
# This prints immediately when the module is imported by uvicorn so it's
# visible in the server console even if lifespan/startup handlers aren't
# producing output for some reason.
try:
    logging.getLogger(__name__).info(
        "[startup-diagnostic] USE_DB=%s _db_loaded=%s",
        getattr(storage, "USE_DB", False),
        getattr(storage, "_db", None) is not None,
    )
except Exception:
    # Best-effort; avoid crashing import if something goes wrong
    logging.getLogger(__name__).info("[startup-diagnostic] failed to evaluate storage diagnostics")

# Ensure src/ is importable if necessary
src_root = Path(__file__).resolve().parents[2] / "src"
if str(src_root) not in sys.path:
    sys.path.insert(0, str(src_root))


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance.

    Returns:
        FastAPI: configured application with CORS and API routes.
    """
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Lifespan context manager initializing optional DB tables.

        FastAPI now recommends using lifespan event handlers instead of
        the `on_event` decorator. We attempt to create DB tables here if
        a database is configured, but we don't prevent the app from
        starting if table creation fails.
        """
        # If DB mode is enabled, verify connectivity and ensure tables exist.
        try:
            if getattr(storage, "USE_DB", False):
                # Ensure DB module imported correctly
                if getattr(storage, "_db", None) is None:
                    msg = "DATABASE_URL is set but DB backend module failed to import."
                    logging.getLogger(__name__).error(msg)
                    raise RuntimeError(msg)

                # Attempt to create tables (will raise on serious failures)
                try:
                    storage._db.create_db_and_tables()
                except Exception as exc:
                    # Surface the error so operator sees it at startup
                    logging.getLogger(__name__).exception("Failed to create DB tables: %s", exc)
                    raise

                # Lightweight connectivity check
                try:
                    from sqlmodel import Session

                    engine = getattr(storage._db, "engine", None)
                    if engine is None:
                        raise RuntimeError("DB engine is not initialized (engine is None)")
                    with Session(engine) as session:  # type: ignore[arg-type]
                        session.exec(text("SELECT 1"))
                except Exception as exc:
                    logging.getLogger(__name__).exception("Database connectivity check failed: %s", exc)
                    raise
        except Exception:
            # Re-raise to stop application startup
            raise
        yield

    app = FastAPI(title="EchoVoice LangGraph API", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8082", "http://127.0.0.1:8082"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    return app


# Export app for `uvicorn api.main:app` usage
app = create_app()
