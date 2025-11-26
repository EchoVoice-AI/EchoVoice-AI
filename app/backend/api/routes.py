"""Top-level router exported to the application.

This module exposes `router` which is included by `app.create_app()`.
"""

from __future__ import annotations

from .routers import router

__all__ = ["router"]
