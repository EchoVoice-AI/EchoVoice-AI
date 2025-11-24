"""Routing utilities for the segmentation phase.

This module provides the goal_router function which examines the current
GraphState to decide which segmentation engine node should run next:
RFM_SEGMENTATION, INTENT_SEGMENTATION, BEHAVIORAL_SEGMENTATION, or
PROFILE_SEGMENTATION (fallback).
"""

import logging
from typing import Literal

from agent.state import GraphState

logger = logging.getLogger(__name__)


def goal_router(state: GraphState) -> Literal[
    "RFM_SEGMENTATION",
    "INTENT_SEGMENTATION",
    "BEHAVIORAL_SEGMENTATION",
    "PROFILE_SEGMENTATION",
]:
    """Route to the appropriate segmentation engine.

    Routes the workflow to the appropriate specialized segmentation engine
    based on the initial 'campaign_goal' or the 'user_message' in the state.

    Args:
        state (GraphState): The current state of the LangGraph.

    Returns:
        Literal: The name of the next segmentation node to execute.
    """
    campaign_goal = (state.get("campaign_goal") or "").lower()
    user_message = (state.get("user_message") or "").lower()

    # --- Rule-Based Routing Logic (Mirroring the Diagram) ---

    # 1. RFM (Recency, Frequency, Monetary) Segmentation
    if "churn" in campaign_goal or "retention" in campaign_goal or "loyalty" in campaign_goal:
        logger.info("Routing to RFM Segmentation (campaign_goal=%s)", campaign_goal)
        return "RFM_SEGMENTATION"

    # 2. INTENT Segmentation (conversational signals)
    if user_message and ("ask" in user_message or "?" in user_message or "tell me about" in user_message):
        logger.info("Routing to INTENT Segmentation (user_message=%s)", user_message)
        return "INTENT_SEGMENTATION"

    # 3. BEHAVIORAL Segmentation
    if "engagement" in campaign_goal or "real-time" in campaign_goal or "activity" in campaign_goal:
        logger.info("Routing to BEHAVIORAL Segmentation (campaign_goal=%s)", campaign_goal)
        return "BEHAVIORAL_SEGMENTATION"

    # 4. PROFILE Segmentation (Default/Fallback)
    logger.info("Routing to PROFILE Segmentation (default)")
    return "PROFILE_SEGMENTATION"


# Note: These return values are the node IDs used when defining conditional edges in app.py.
