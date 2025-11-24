"""State for deployment phase."""
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class DeploymentState:
    """Shared state for the deployment phase."""
    deployed_versions: Dict[str, Any] = field(default_factory=dict)
    feedback_loop: Dict[str, Any] = field(default_factory=dict)
