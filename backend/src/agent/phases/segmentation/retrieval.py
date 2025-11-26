"""Segmentation retrieval node implementations.

This module contains a lightweight retrieval node used by the segmentation
phase to gather contextual documents or signals for downstream nodes.
It is intentionally minimal in the example repository.
"""

from typing import Any, Dict, List

from langgraph.runtime import Runtime

from agent.state import Context, GraphState


async def retrieval_node(state: GraphState, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Simulate fetching relevant context/documents for critical segments.

    Returns keys `context_query` and `retrieved_content` to be merged into the
    GraphState for later nodes.
    """
    final_segment = state.get("final_segment")

    # 1. Formulate a search query based on the segment and campaign goal
    query = f"Critical document review for segment: {final_segment} related to goal: {state.get('campaign_goal')}"

    # 2. Simulate document fetching (e.g., hitting a Vector DB)
    retrieved_docs: List[Dict[str, str]] = [
        {"source": "Policy Doc 4.1", "text": "Terms of the High-Value Customer Retention Offer are valid for 30 days."},
        {"source": "System Log 2025", "text": "Recent system logs show error code 503 during checkout for this user."},
    ]

    return {
        "context_query": query,
        "retrieved_content": retrieved_docs,
    }