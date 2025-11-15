"""Simple orchestrator to run nodes in sequence."""
from typing import List, Any
from app.nodes.base_node import BaseNode
from services.logger import get_logger

logger = get_logger(__name__)

class Orchestrator:
    """Orchestrator that manages and runs a list of nodes."""

    def __init__(self):
        self.nodes: List[BaseNode] = []

    def add_node(self, node: BaseNode) -> None:
        """Add a node to the execution graph."""
        self.nodes.append(node)

    def run(self, input_data: Any) -> Any:
        """Run all nodes in sequence, passing output of each to the next."""
        data = input_data
        for node in self.nodes:
            try:
                data = node.run(data)
            except Exception as e:
                logger.error(f"Error executing node '{node.name}': {type(e).__name__}: {str(e)}")
                raise
        return data
