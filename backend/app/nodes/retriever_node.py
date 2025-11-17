from typing import Any

from .base_node import BaseNode
from agents.retriever import retrieve_citations


class RetrieverNode(BaseNode):
    """Node wrapper for the retrieval agent.

    Expects `data` to be a customer dict passed to `retrieve_citations`.
    """

    def __init__(self, name: str = "retriever"):
        super().__init__(name)

    def run(self, data: Any) -> Any:
        return retrieve_citations(data)
