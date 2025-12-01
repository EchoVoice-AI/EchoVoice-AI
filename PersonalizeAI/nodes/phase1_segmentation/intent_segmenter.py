"""Intent-based segmenter - simple example.

Exposes `run(state)` that appends candidate segment(s).
"""
from typing import Dict


def run(state: Dict) -> Dict:
    msg = (state.get("user_message") or "").lower()

    if any(k in msg for k in ("buy", "purchase", "pricing", "price")):
        segment = "purchase_intent"
        desc = "Users expressing purchase intent."
        confidence = 0.8
    elif any(k in msg for k in ("info", "learn", "learn more", "details")):
        segment = "researchers"
        desc = "Users researching or learning about products."
        confidence = 0.6
    else:
        segment = "general_interest"
        desc = "General interest / engagement segment."
        confidence = 0.5

    state.setdefault("candidate_segments", []).append({
        "id": segment,
        "description": desc,
        "confidence": confidence,
        "source": "INTENT_SEGMENTATION",
    })

    return state
