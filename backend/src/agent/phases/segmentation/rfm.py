"""RFM segmentation node (explainable template).

This module provides a concrete example of a Phase-1 segmentation node.
The function `rfm_segmenter` returns a structured payload containing
the label, confidence and a human-readable justification that downstream
nodes (priority, generation) will consume.
"""
from __future__ import annotations

import logging
from typing import Any, Dict

from langgraph.runtime import Runtime
from langsmith import traceable

from agent.state import Context, GraphState

logger = logging.getLogger(__name__)

@traceable
def rfm_segmenter(state: GraphState) -> Dict[str, Any]:
    """Analyze Recency/Frequency/Monetary signals and return explainable output.

    Args:
        state: Shared GraphState containing inputs such as `user_message` and
            any enrichment data available on the state.

    Returns:
        A dict with `raw_segmentation_data` keyed by the segment type.
    """
    # --- SIMULATE RFM CALCULATION / LLM SEGMENTATION ---
    segment_type = "rfm"

    # Example logic (placeholder): determine an RFM label and confidence.
    # If the campaign explicitly signals retention/churn, prefer a retention candidate.
    campaign_goal = (state.get("campaign_goal") or "").lower() if isinstance(state, dict) else ""
    if any(k in campaign_goal for k in ("churn", "retention", "retain", "loyalty")):
        segment_label = "retention_candidate"
        confidence_score = 0.9
        justification = (
            "Campaign goal explicitly signals retention/churn. "
            "Marking user as a retention candidate to prioritize retention messaging and offers."
        )
    else:
        # Fallback placeholder behavior
        segment_label = "High Engagement, Low Spend"
        confidence_score = 0.75
        justification = (
            "This user is classified as a 'High Engagement, Low Spend' RFM segment. "
            "They interact frequently with our content but their average order value is below average. "
            "Targeting should focus on increasing basket size or high-margin product upsell."
        )

    logger.info("RFM Segmentation complete: %s (Confidence: %.2f)", segment_label, confidence_score)

    return {
        "rfm_segment_output": { # <--- UNIQUE KEY FOR RFM
            "label": segment_label,
            "confidence": confidence_score,
            "justification": justification,
        }
    }

async def rfm_segmentor_node(state: GraphState, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Produce RFM segmentation."""
    return rfm_segmenter(state)
    