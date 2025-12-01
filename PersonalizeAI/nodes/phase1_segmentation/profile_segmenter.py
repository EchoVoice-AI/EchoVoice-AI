"""Profile-based segmenter - simple example.

Exposes `run(state)` that appends candidate segment(s).
"""
from typing import Dict


def run(state: Dict) -> Dict:
    # Example profile segmentation: check for demographic keywords
    goal = (state.get("campaign_goal") or "").lower()

    if "enterprise" in goal or "b2b" in goal:
        segment = "enterprise_accounts"
        desc = "Enterprise / B2B customer profile."
        confidence = 0.8
    elif "student" in goal or "education" in goal:
        segment = "education"
        desc = "Education / student segment."
        confidence = 0.6
    else:
        segment = "consumer"
        desc = "General consumer profile."
        confidence = 0.5

    state.setdefault("candidate_segments", []).append({
        "id": segment,
        "description": desc,
        "confidence": confidence,
        "source": "PROFILE_SEGMENTATION",
    })

    return state
