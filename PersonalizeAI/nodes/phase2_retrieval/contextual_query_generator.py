"""Contextual Query Generator (Phase 2)

Generates a concise, vector-search-friendly `context_query` from the
`segment_description` and `campaign_goal` fields in the shared GraphState.
"""
from typing import Dict, Any
from PersonalizeAI.state import GraphState


def contextual_query_generator(state: GraphState) -> Dict[str, Any]:
    """Produce an optimized vector search query and return an update dict.

    This is a small heuristic/LLM-call simulation. Real deployments should
    call an LLM with a carefully crafted prompt.
    """
    segment_desc = (state.get("segment_description") or "").lower()
    campaign_goal = (state.get("campaign_goal") or "").lower()

    # --- Heuristic / LLM-simulated logic ---
    if "high value" in segment_desc and "clarification" in segment_desc:
        query = "product facts high-value shopper nutritional details"
    elif "churn" in campaign_goal or "reduce churn" in campaign_goal:
        query = "product features for customer retention"
    else:
        query = "general product information"

    print(f"Generated Query: '{query}'")

    # return partial state update
    return {"context_query": query}
