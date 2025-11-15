"""Simple orchestrator to run nodes in sequence."""
from typing import List, Any
from backend.app.nodes.base_node import BaseNode

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
            data = node.run(data)
        return data
