"""Segmentation retrieval node implementations.

This module contains a lightweight retrieval node used by the segmentation
phase to gather contextual documents or signals for downstream nodes.
It is intentionally minimal in the example repository.
"""

from typing import Any, Dict, List

from langgraph.runtime import Runtime

from agent.state import Context, GraphState

from agent.services.retriever import run_retriever_chain
from api import storage


async def retrieval_node(state: GraphState, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Fetch relevant documents using configured retrievers.

    This implementation prefers configured retrievers (Azure Search, etc.)
    and falls back to a small set of mock results when none are configured
    or when retrieval fails.
    """
    final_segment = state.get("final_segment")

    # 1. Formulate a search query based on the segment and campaign goal
    query = f"Critical document review for segment: {final_segment} related to goal: {state.get('campaign_goal')}"

    # 2. Load configured retrievers from storage
    retrievers = storage.load_retrievers() or []

    if retrievers:
        try:
            # context may provide an embedding vector under `query_vector` if available
            context = {"final_segment": final_segment, **(state.get("event_metadata", {}))}
            docs = await run_retriever_chain(retrievers, query, context, k=5, timeout=6.0, deterministic_key=state.get("event_metadata", {}).get("user_id"))
            if docs:
                return {"context_query": query, "retrieved_content": docs}
        except Exception:
            # fall through to mock
            pass

    # Fallback mock documents
    retrieved_docs: List[Dict[str, str]] = [
        {"source": "Policy Doc 4.1", "text": "Terms of the High-Value Customer Retention Offer are valid for 30 days."},
        {"source": "System Log 2025", "text": "Recent system logs show error code 503 during checkout for this user."},
    ]

    return {
        "context_query": query,
        "retrieved_content": retrieved_docs,
    }