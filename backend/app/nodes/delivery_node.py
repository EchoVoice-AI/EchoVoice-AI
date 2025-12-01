from typing import Any, Dict

from .base_node import BaseNode
from agents.delivery_agent import deliver_for_user


class DeliveryNode(BaseNode):
    """Node wrapper for the delivery agent.

    Expects `data` to be a dict with keys: `customer`, `safety`, `analysis`,
    `variants`, and optional `options`.
    """

    def __init__(self, name: str = "delivery"):
        super().__init__(name)

    def run(self, data: Any) -> Dict[str, Any]:
        # Allow either dict-shaped input or raw payload
        context = data if isinstance(data, dict) else {"payload": data}

        # delivery agent handles safety/analysis/variants and returns a result dict
        result = deliver_for_user(context)
        return result
