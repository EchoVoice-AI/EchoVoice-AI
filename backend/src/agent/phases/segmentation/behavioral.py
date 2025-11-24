"""Behavioral segmentation node (explainable template)."""
from __future__ import annotations

import logging
from typing import Any, Dict

from agent.state import GraphState

logger = logging.getLogger(__name__)


def behavioral_segmenter(state: GraphState) -> Dict[str, Any]:
    """Analyze behavior signals and return structured segmentation output."""
    segment_type = "behavioral"
    segment_label = "neutral"
    confidence_score = 0.5
    justification = (
        "User interaction patterns are typical with no strong emotional cues. "
        "No escalation or special handling required; apply standard content tuning."
    )

    logger.info("Behavioral segmentation complete: %s (%.2f)", segment_label, confidence_score)

    return {
        "raw_segmentation_data": {
            segment_type: {
                "label": segment_label,
                "confidence": confidence_score,
                "justification": justification,
            }
        }
    }


def segment_behavioral(context: Dict[str, Any]) -> Dict[str, Any]:
    """Build a temporary GraphState from the given context and run behavioral segmentation."""
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
    return behavioral_segmenter(fake_state)

