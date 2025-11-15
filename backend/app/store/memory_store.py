"""Simple in-memory key/value store for orchestrator."""
from typing import Any, Dict

class MemoryStore:
    """A tiny in-memory store used by the orchestrator for transient state."""

    def __init__(self):
        self._store: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)
