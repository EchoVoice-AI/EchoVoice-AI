"""Relevance Grader (Phase 2 conditional router).

Acts as an LLM-as-a-Judge simulation; returns the next node id based on
whether retrieved content contains product facts relevant to the segment.
"""
from typing import Dict
from PersonalizeAI.state import GraphState


def relevance_grader(state: GraphState) -> str:
    """Return either 'CITATION_FORMATTER' or 'SELF_CORRECTION'."""
    retrieved_content = state.get("retrieved_content", []) or []
    segment_desc = (state.get("segment_description") or "").lower()

    is_relevant = False

    # Simple rule: if any snippet contains common product keywords, mark relevant
    for doc in retrieved_content:
        text = (doc.get("text") or "").lower()
        if any(k in text for k in ("protein", "sugar", "ingredient", "feature")):
            is_relevant = True
            break

    # Prevent infinite loops by honoring a attempts counter
    if state.get("retrieval_attempts", 0) >= 3:
        print("Max retrieval attempts reached. Proceeding with best available content.")
        is_relevant = True

    if is_relevant:
        print("Relevance Grade: YES. Content is sufficient.")
        return "CITATION_FORMATTER"
    else:
        state["retrieval_attempts"] = state.get("retrieval_attempts", 0) + 1
        print(f"Relevance Grade: NO. Attempt {state['retrieval_attempts']}. Rewriting query.")
        return "SELF_CORRECTION"
