"""State for generation phase"""
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class GenerationState:
    messages: Dict[str, Any] = field(default_factory=dict)
    safety_flags: Dict[str, Any] = field(default_factory=dict)
