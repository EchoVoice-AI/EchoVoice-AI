"""Shared GraphState TypedDict for PersonalizeAI nodes.

This file contains a minimal typed representation used across LangGraph nodes.
Fields are optional to keep nodes lightweight for this demo scaffolding.
"""
from typing import TypedDict, Any, Optional


class GraphState(TypedDict, total=False):
    campaign_goal: str
    user_message: str

    # Phase 1 outputs
    candidate_segments: list[dict]
    final_segment: str
    confidence: float
    segment_description: str
    final_segment_source: str

    # Phase 2/3/4 fields (placeholders)
    context_query: Optional[str]
    retrieved_content: Optional[Any]
    message_variants: Optional[list]
    compliance_log: Optional[list]
    winning_variant_id: Optional[str]
    predicted_performance: Optional[dict]
    feedback_payload: Optional[dict]
