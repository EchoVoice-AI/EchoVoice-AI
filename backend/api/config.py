"""Central configuration and environment loading for the API package.

This module loads a local `.env` (if present) once and provides a small
`Settings` object for other modules to import. Keeping a single loader
prevents race conditions where modules read `os.environ` before dotenv
has been processed.
"""
from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - optional dependency
    load_dotenv = None  # type: ignore


class Settings:
    """Lightweight container for environment settings.

    Read values from the process environment. This deliberately avoids
    heavier dependencies so it's safe to import early during app startup.
    """

    def __init__(self) -> None:
        # Attempt to load the `.env` file located in the backend package
        # directory so values defined there are available to other modules.
        env_path = Path(__file__).resolve().parents[1] / ".env"
        if load_dotenv is not None and env_path.exists():
            # Do not override variables already set in the environment.
            load_dotenv(dotenv_path=env_path, override=False)

        self.DATABASE_URL: str | None = os.environ.get("DATABASE_URL")
        self.LANGSMITH_API_KEY: str | None = os.environ.get("LANGSMITH_API_KEY")
        self.API_HOST: str = os.environ.get("API_HOST", "github")

    @property
    def use_db(self) -> bool:
        return bool(self.DATABASE_URL)


# Single shared settings instance for importers to use (import-time safe)
SETTINGS = Settings()
