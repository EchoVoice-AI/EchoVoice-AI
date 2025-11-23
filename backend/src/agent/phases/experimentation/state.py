"""State for experimentation phase"""
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class ExperimentState:
    experiments: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
