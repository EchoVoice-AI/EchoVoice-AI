"""Application factory and ASGI `app` for the EchoVoice API.

This module creates the FastAPI application, configures CORS, and
includes the route definitions from `routes.py`.
"""

from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import SETTINGS

_ = SETTINGS

# Ensure environment is loaded before importing modules that may read it.
# Import storage after SETTINGS exists so it sees the loaded env.
from . import storage
from .routes import router as api_router

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
        try:
            if getattr(storage, "USE_DB", False) and getattr(storage, "_db", None) is not None:
                try:
                    storage._db.create_db_and_tables()
                except Exception:
                    # allow server to start even if DB init fails; errors will
                    # surface when the DB is used.
                    pass
        except Exception:
            pass
        yield

    app = FastAPI(title="EchoVoice LangGraph API", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    return app


# Export app for `uvicorn api.main:app` usage
app = create_app()
