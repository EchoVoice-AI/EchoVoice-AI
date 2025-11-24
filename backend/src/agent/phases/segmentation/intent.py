"""Intent segmentation node (explainable template).

Provides an example intent segmentation node that produces a
label, confidence and human-readable justification for downstream use.
"""
from __future__ import annotations

import logging
from typing import Any, Dict

from agent.state import GraphState

logger = logging.getLogger(__name__)


def intent_segmenter(state: GraphState) -> Dict[str, Any]:
    """Analyze user_message or context to extract intent and justification.

    Returns a structured `raw_segmentation_data` payload similar to other
    phase-1 segmentation nodes.
    """
    segment_type = "intent"
    segment_label = "clarification"
    confidence_score = 0.88
    justification = (
        "User asked a clarifying question or requested more information. "
        "Intent extracted indicates the user seeks factual clarification; "
        "responses should be concise and evidence-backed."
    )

    logger.info("Intent segmentation complete: %s (%.2f)", segment_label, confidence_score)

    return {
        "raw_segmentation_data": {
            segment_type: {
                "label": segment_label,
                "confidence": confidence_score,
                "justification": justification,
            }
        }
    }


def segment_intent(context: Dict[str, Any]) -> Dict[str, Any]:
    """Build a temporary GraphState from the given context and run intent segmentation."""
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
    return intent_segmenter(fake_state)

