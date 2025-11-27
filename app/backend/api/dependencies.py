"""API dependencies for authentication and authorization."""
import logging
from typing import Any

from fastapi import HTTPException, Request

from config import CONFIG_AUTH_CLIENT, CONFIG_SEARCH_CLIENT
from core.authentication import AuthError


async def get_auth_claims(request: Request) -> dict[str, Any]:
    """FastAPI dependency to replace `@authenticated` decorator.

    Returns an `auth_claims` dict (possibly empty) or raises HTTPException(403)
    when authentication is required but invalid.
    """
    cfg = getattr(request.app.state, "config", {})
    auth_helper = cfg.get(CONFIG_AUTH_CLIENT)
    if not auth_helper:
        # No auth helper configured -> treat as unauthenticated but allowed
        return {}

    try:
        # Convert headers to plain dict; the helper expects a dict-like object
        headers = dict(request.headers)
        auth_claims = await auth_helper.get_auth_claims_if_enabled(headers)
        return auth_claims
    except AuthError:
        # Mirror previous behavior (decorator aborted with 403 on AuthError)
        raise HTTPException(status_code=403)
    except Exception as exc:
        logging.exception("Problem checking auth claims: %s", exc)
        # For other errors, return 500 so clients see server error
        raise HTTPException(status_code=500, detail=str(exc))


async def require_path_auth(path: str, request: Request) -> dict[str, Any]:
    """Dependency used by routes that need to check access to a specific path.

    Returns auth_claims if authorized, raises HTTPException(403) if not.
    """
    cfg = getattr(request.app.state, "config", {})
    auth_helper = cfg.get(CONFIG_AUTH_CLIENT)
    search_client = cfg.get(CONFIG_SEARCH_CLIENT)
    if not auth_helper:
        return {}

    try:
        headers = dict(request.headers)
        auth_claims = await auth_helper.get_auth_claims_if_enabled(headers)
        authorized = await auth_helper.check_path_auth(path, auth_claims, search_client)
        if not authorized:
            raise HTTPException(status_code=403)
        return auth_claims
    except AuthError:
        raise HTTPException(status_code=403)
    except Exception as exc:
        logging.exception("Problem checking path auth: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
