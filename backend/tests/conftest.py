import os
from pathlib import Path

import pytest

try:
    from dotenv import load_dotenv

    # Attempt to load a .env file located at the backend package root so pytest
    # sees the same environment variables that `langgraph dev` (which reads
    # `langgraph.json` -> `.env`) provides.
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except Exception:
    # If python-dotenv is not available or loading fails, proceed without it.
    pass


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


def pytest_collection_modifyitems(config, items):
    """Skip tests marked with 'langsmith' if no LangSmith/LangChain API key is set.

    This prevents integration tests that call the LangSmith API from failing with
    HTTP 401 errors during local runs where an API key isn't configured.
    """
    if os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY"):
        return

    skip_marker = pytest.mark.skip(reason="LangSmith API key not set; skipping langsmith tests")
    for item in items:
        if "langsmith" in item.keywords:
            item.add_marker(skip_marker)
