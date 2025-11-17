from typing import Any

from .base_node import BaseNode
from agents.analytics import evaluate_variants


class AnalyticsNode(BaseNode):
    """Node wrapper for analytics/evaluation.

    Expects `data` to be a dict with keys `variants` and `customer`.
    """

    def __init__(self, name: str = "analytics"):
        super().__init__(name)

    def run(self, data: Any) -> Any:
        if isinstance(data, dict):
            variants = data.get("variants")
            customer = data.get("customer")
        else:
            variants = data
            customer = None
        return evaluate_variants(variants, customer)
