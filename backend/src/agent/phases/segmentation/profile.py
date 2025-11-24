"""Profile segmentation node (explainable template)."""
from __future__ import annotations

import logging
from typing import Any, Dict

from agent.state import GraphState

logger = logging.getLogger(__name__)


def profile_segmenter(state: GraphState) -> Dict[str, Any]:
    """Analyze user profile attributes and return structured segmentation output."""
    segment_type = "profile"
    segment_label = "general"
    confidence_score = 0.6
    justification = (
        "Profile-based segmentation indicates a general user profile with no "
        "specialization detected. Use default verbosity and formatting."
    )

    logger.info("Profile segmentation complete: %s (%.2f)", segment_label, confidence_score)

    return {
        "raw_segmentation_data": {
            segment_type: {
                "label": segment_label,
                "confidence": confidence_score,
                "justification": justification,
            }
        }
    }


def segment_profile(context: Dict[str, Any]) -> Dict[str, Any]:
    """Build a temporary GraphState from the given context and run profile segmentation.

    Parameters
    ----------
    context : Dict[str, Any]
        Input context containing optional keys such as 'campaign_goal', 'text', or
        'user_message' that are used to populate a fake GraphState for the segmenter.

    Returns:
    -------
    Dict[str, Any]
        The segmentation result produced by profile_segmenter, typically containing
        'raw_segmentation_data' with label, confidence and justification.
    """
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
    return profile_segmenter(fake_state)

