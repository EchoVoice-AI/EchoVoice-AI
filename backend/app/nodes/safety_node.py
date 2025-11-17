from typing import Any

from .base_node import BaseNode
from agents.safety_gate import safety_check_and_filter


class SafetyNode(BaseNode):
    """Node wrapper for the safety gate.

    Expects `data` to be a list of variants (or dict with 'variants' key).
    """

    def __init__(self, name: str = "safety"):
        super().__init__(name)

    def run(self, data: Any) -> Any:
        variants = data if not isinstance(data, dict) else data.get("variants")
        return safety_check_and_filter(variants)
