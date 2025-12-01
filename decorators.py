import functools
import inspect
from typing import Any, Callable


def authenticated(func: Callable) -> Callable:
    """Lightweight shim for the `@authenticated` decorator used in the app.

    In production this enforces authentication and injects `auth_claims` into
    the decorated handler. For tests and local runs this shim simply calls the
    handler and injects an empty dict for `auth_claims` if the handler accepts
    that argument name.
    """

    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            if 'auth_claims' in sig.parameters and 'auth_claims' not in kwargs:
                kwargs['auth_claims'] = {}
            return await func(*args, **kwargs)

        return async_wrapper

    else:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            if 'auth_claims' in sig.parameters and 'auth_claims' not in kwargs:
                kwargs['auth_claims'] = {}
            return func(*args, **kwargs)

        return sync_wrapper


__all__ = ["authenticated"]

# Backwards-compatible alias expected by the backend code
authenticated_path = authenticated
__all__.append("authenticated_path")
