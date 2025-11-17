"""Redis-backed store adapter matching MemoryStore API.

This adapter is optional. `app.store` will attempt to use Redis when
`app.config.REDIS_URL` is set and the `redis` package is available.
"""
from typing import Any, Optional
import json

try:
    import redis
except Exception:  # pragma: no cover - optional dependency
    redis = None  # type: ignore


class RedisStore:
    """A simple Redis-backed store that stores JSON-serializable values.

    Note: values must be JSON-serializable. For arbitrary Python objects
    consider a different serializer or adapter.
    """

    def __init__(self, url: str) -> None:
        if redis is None:
            raise RuntimeError("redis package is not installed")
        self._client = redis.from_url(url)

    def set(self, key: str, value: Any) -> None:
        payload = json.dumps(value)
        self._client.set(key, payload)

    def get(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        raw = self._client.get(key)
        if raw is None:
            return default
        try:
            return json.loads(raw)
        except Exception:
            return default

    def delete(self, key: str) -> None:
        self._client.delete(key)
