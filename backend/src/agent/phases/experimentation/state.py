"""State for experimentation phase."""
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class ExperimentState:
    """Shared state for the experimentation phase."""
    experiments: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
