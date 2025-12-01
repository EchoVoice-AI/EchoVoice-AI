"""RFM segmenter - simple rule-based example.

This module exposes `run(state)` which returns an updated GraphState.
"""
from typing import Dict


def run(state: Dict) -> Dict:
    # Very simple RFM-like logic based on keywords in user_message or campaign_goal
    msg = (state.get("user_message") or "").lower()
    goal = (state.get("campaign_goal") or "").lower()

    if "churn" in msg or "churn" in goal:
        segment = "at_risk"
        desc = "Customers likely to churn (RFM: low recency/high churn signals)."
        confidence = 0.7
    else:
        segment = "high_value"
        desc = "High value customers based on recent/large purchases."
        confidence = 0.6

    state.setdefault("candidate_segments", []).append({
        "id": segment,
        "description": desc,
        "confidence": confidence,
        "source": "RFM_SEGMENTATION",
    })

    return state
