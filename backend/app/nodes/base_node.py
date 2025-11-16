"""Base node interface for orchestrator nodes."""
from abc import ABC, abstractmethod
from typing import Any

class BaseNode(ABC):
    """Abstract base class for orchestrator nodes."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def run(self, data: Any) -> Any:
        """Process `data` and return the result.

        Subclasses must implement this method.
        """
        raise NotImplementedError()
