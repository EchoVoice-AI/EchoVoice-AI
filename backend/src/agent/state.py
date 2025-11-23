from dataclasses import dataclass
from typing import Any, Dict, List, TypedDict


# --- Core State Definition ---
@dataclass
class GraphState(TypedDict):
    """Represents the shared state of the LangGraph pipeline, passed between all nodes.

    Defines the initial structure of incoming data.
    See: https://langchain-ai.github.io/langgraph/concepts/low_level/#state
    """
    # Phase 1: Segmentation (Input & Output)
    campaign_goal: str                      # Initial input (e.g., 'reduce_churn', 'increase_upsell')
    user_message: str | None                 # Conversational input, if applicable
    final_segment: str                      # E.g., 'RFM:HighValue'
    confidence: float                       # Confidence score for the final segment
    segment_description: str                # Human-readable justification for explainability

    # Phase 2: Content Retrieval
    context_query: str | None                # Query generated for vector search
    retrieved_content: List[Dict[str, str]] # List of {text: ..., source_id: ...}

    # Phase 3: Message Generation & Compliance
    message_variants: List[Dict[str, str]]  # A/B/n messages (Subject, Body, CTA)
    compliance_log: List[Dict[str, Any]]    # Record of safety checks and violations

    # Phase 4: Experimentation & Feedback
    winning_variant_id: str | None           # ID of the message chosen for deployment
    predicted_performance: Dict[str, Any]   # Predicted metrics (CTR, Lift) for the winner
    feedback_payload: Dict[str, Any]        # Structured data for the learning loop


__all__ = ["GraphState"]
