"""Simple in-memory key/value store for orchestrator.

This store is intentionally tiny and suitable for transient state during
orchestration. It is guarded by a simple `threading.Lock` to make basic
concurrent access safe when the orchestrator is handling multiple requests
in different threads/workers.
"""
from typing import Any, Dict, Optional
import threading


class MemoryStore:
    """A tiny in-memory store used by the orchestrator for transient state.

    Thread-safe via an internal Lock. Methods are type-hinted to improve
    IDE/editor support and simplify reasoning about usage.
    """

    def __init__(self) -> None:
        self._store: Dict[str, Any] = {}
        self._lock = threading.Lock()

    def set(self, key: str, value: Any) -> None:
        """Set a value for `key` in the store."""
        with self._lock:
            self._store[key] = value

    def get(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        """Return the value for `key` or `default` if not present."""
        with self._lock:
            return self._store.get(key, default)

    def delete(self, key: str) -> None:
        """Remove `key` from the store if present."""
        with self._lock:
            self._store.pop(key, None)
