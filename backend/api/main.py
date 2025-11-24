"""Main entrypoint for ASGI servers.

This module simply exposes the application instance `app` created in
`.app.create_app()` so that Uvicorn/Gunicorn can import `api.main:app`.
"""

from .app import app

