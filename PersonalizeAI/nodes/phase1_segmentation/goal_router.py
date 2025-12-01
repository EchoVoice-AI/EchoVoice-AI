"""Simple rule-based goal router for Phase 1 segmentation.

Returns the node id to run next given the GraphState.
"""
from typing import Dict


def goal_router(state: Dict) -> str:
    """Return a segmentation node id based on campaign_goal or user_message.

    Possible return values: RFM_SEGMENTATION, INTENT_SEGMENTATION,
    BEHAVIORAL_SEGMENTATION, PROFILE_SEGMENTATION
    """
    goal = (state.get("campaign_goal") or "").lower()
    msg = (state.get("user_message") or "").lower()

    # Priority: explicit keywords in the campaign_goal, then user_message
    if any(k in goal for k in ("rfm", "recency", "monetary", "frequency")):
        return "RFM_SEGMENTATION"

    if any(k in goal for k in ("intent", "buy", "pricing", "purchase")) or any(k in msg for k in ("buy", "purchase", "pricing")):
        return "INTENT_SEGMENTATION"

    if any(k in goal for k in ("behavior", "engagement", "demo", "trial")) or any(k in msg for k in ("demo", "trial", "signup")):
        return "BEHAVIORAL_SEGMENTATION"

    # Fallback to profile-based segmentation when campaign is audience/profile oriented
    return "PROFILE_SEGMENTATION"
