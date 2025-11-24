
"""EchoVoice-AI backend API package.

This package exposes the ASGI `app` object for Uvicorn/ASGI servers
and keeps the API split across modules for clarity.
"""

from .app import app

__all__ = ["app"]

