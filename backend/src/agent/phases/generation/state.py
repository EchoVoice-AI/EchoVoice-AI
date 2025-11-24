"""State for generation phase."""
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class GenerationState:
    """Shared state for the generation phase."""
    messages: Dict[str, Any] = field(default_factory=dict)
    safety_flags: Dict[str, Any] = field(default_factory=dict)
