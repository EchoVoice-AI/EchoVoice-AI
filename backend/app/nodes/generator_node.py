from typing import Any

from .base_node import BaseNode
from agents.generator import generate_variants


class GeneratorNode(BaseNode):
    """Node wrapper for the generation agent.

    Expects `data` to be a dict with keys: `customer`, `segment`, `citations`.
    """

    def __init__(self, name: str = "generator"):
        super().__init__(name)

    def run(self, data: Any) -> Any:
        customer = data.get("customer") if isinstance(data, dict) else data
        segment = data.get("segment") if isinstance(data, dict) else None
        citations = data.get("citations") if isinstance(data, dict) else None

        # Accept either a string segment label or a segment dict
        if isinstance(segment, str):
            segment = {"segment": segment}

        # Provide safe defaults so underlying agent code won't raise
        if customer is None:
            customer = {}
        if segment is None:
            segment = {}
        if citations is None:
            citations = []

        return generate_variants(customer, segment, citations)
