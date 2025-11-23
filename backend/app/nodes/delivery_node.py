from __future__ import annotations

from typing import Any, Dict, Optional

from .base_node import BaseNode
from agents.delivery_agent import DeliveryAgent


class DeliveryNode(BaseNode):
    """LangGraph node adapter for the DeliveryAgent.

    Expects `data` to contain at least:
      - customer: dict with `email` key
      - variant: dict with `subject` and `body` keys
    """

    def __init__(self, name: str = "delivery", agent: Optional[DeliveryAgent] = None):
        super().__init__(name)
        self.agent = agent or DeliveryAgent()

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        customer = data.get("customer") or {}
        variant = data.get("variant") or {}

        to_email = customer.get("email")
        subject = variant.get("subject")
        body = variant.get("body")

        if not to_email or not subject or not body:
            return {"status": "skipped", "reason": "missing_fields"}

        result = self.agent.deliver(to_email, subject, body)
        return result
