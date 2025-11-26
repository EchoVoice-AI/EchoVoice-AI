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
        """Load environment variables from .env and os.environ."""
        # Attempt to load the `.env` file located in the backend package
        # directory so values defined there are available to other modules.
        env_path = Path(__file__).resolve().parents[1] / ".env"
        if load_dotenv is not None and env_path.exists():
            # Do not override variables already set in the environment.
            load_dotenv(dotenv_path=env_path, override=False)

        self.DATABASE_URL: str | None = os.environ.get("DATABASE_URL")
        self.LANGSMITH_API_KEY: str | None = os.environ.get("LANGSMITH_API_KEY")
        self.API_HOST: str = os.environ.get("API_HOST", "github")
        # Concurrency limit for async graph runs
        self.MAX_CONCURRENT_RUNS: int = int(os.environ.get("MAX_CONCURRENT_RUNS", "4"))
        # Azure Blob Storage settings
        self.AZURE_STORAGE_CONNECTION_STRING: str | None = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
        self.AZURE_STORAGE_CONTAINER: str = os.environ.get("AZURE_STORAGE_CONTAINER", "echovoice-uploads")

    @property
    def use_db(self) -> bool:
        """Indicate whether a database is configured for use."""
        return bool(self.DATABASE_URL)

    @property
    def max_concurrent_runs(self) -> int:
        """Get the maximum number of concurrent runs allowed."""
        return int(self.MAX_CONCURRENT_RUNS)

    @property
    def azure_storage_connection_string(self) -> str | None:
        """Get the Azure Storage connection string."""
        return self.AZURE_STORAGE_CONNECTION_STRING

    @property
    def azure_storage_container(self) -> str:
        """Get the Azure Storage container name."""
        return self.AZURE_STORAGE_CONTAINER


# Single shared settings instance for importers to use (import-time safe)
SETTINGS = Settings()
