"""State for deployment phase"""
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class DeploymentState:
    deployed_versions: Dict[str, Any] = field(default_factory=dict)
    feedback_loop: Dict[str, Any] = field(default_factory=dict)
