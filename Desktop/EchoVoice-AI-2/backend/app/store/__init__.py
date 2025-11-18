"""Store package for orchestrator backend.

Expose a process-local singleton `store` for simple global access. Code
should import the instance via `from app.store import store` or use the
`MemoryStore` type if they need annotations.
"""
from typing import Optional
from .memory_store import MemoryStore
from .redis_store import RedisStore
from app import config


def _create_store() -> MemoryStore:
	"""Return a store instance. If REDIS is configured, attempt to use it.

	Falls back to the in-memory store if Redis is not available or fails
	to initialize.
	"""
	redis_url: Optional[str] = getattr(config, "REDIS_URL", None) or None
	if redis_url:
		try:
			return RedisStore(redis_url)  # type: ignore[return-value]
		except Exception:
			# Fall back to in-memory store on any Redis initialization error
			pass
	return MemoryStore()


# Singleton store instance for global use within the backend/orchestrator.
store = _create_store()

__all__ = ["MemoryStore", "store"]
