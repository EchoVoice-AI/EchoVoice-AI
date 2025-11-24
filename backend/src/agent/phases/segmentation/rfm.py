"""RFM segmentation node (explainable template).

This module provides a concrete example of a Phase-1 segmentation node.
The function `rfm_segmenter` returns a structured payload containing
the label, confidence and a human-readable justification that downstream
nodes (priority, generation) will consume.
"""
from __future__ import annotations

import logging
from typing import Any, Dict

from agent.state import GraphState

logger = logging.getLogger(__name__)


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

    # Example logic (placeholder): determine an RFM label and confidence
    segment_label = "High Engagement, Low Spend"
    confidence_score = 0.75

    # Explainable justification
    justification = (
        "This user is classified as a 'High Engagement, Low Spend' RFM segment. "
        "They interact frequently with our content but their average order value is below average. "
        "Targeting should focus on increasing basket size or high-margin product upsell."
    )

    logger.info("RFM Segmentation complete: %s (Confidence: %.2f)", segment_label, confidence_score)

    return {
        "raw_segmentation_data": {
            segment_type: {
                "label": segment_label,
                "confidence": confidence_score,
                "justification": justification,
            }
        }
    }


# Backwards-compatible wrapper expected by other modules
def segment_rfm(context: Dict[str, Any]) -> Dict[str, Any]:
    """Backwards-compatible wrapper that accepts a simple context dict and delegates to rfm_segmenter.

    This function builds a minimal GraphState-like dictionary from the provided
    context so callers that previously passed a plain dict remain supported.

    Parameters
    ----------
    context : Dict[str, Any]
        Input context which may contain 'campaign_goal', 'text' or 'user_message'
        and other optional keys.

    Returns:
    -------
    Dict[str, Any]
        The segmentation payload produced by rfm_segmenter, containing
        'raw_segmentation_data' keyed by the segment type.
    """
    # allow callers that pass a simple context dict
    fake_state: GraphState = {
        "campaign_goal": context.get("campaign_goal", ""),
        "user_message": context.get("text") or context.get("user_message"),
        "final_segment": "",
        "confidence": 0.0,
        "segment_description": "",
        "context_query": None,
        "retrieved_content": [],
        "message_variants": [],
        "compliance_log": [],
        "winning_variant_id": None,
        "predicted_performance": {},
        "feedback_payload": {},
    }
    return rfm_segmenter(fake_state)
