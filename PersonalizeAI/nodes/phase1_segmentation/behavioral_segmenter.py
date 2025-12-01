"""Behavioral segmenter - simple example.

Exposes `run(state)` that appends candidate segment(s).
"""
from typing import Dict


def run(state: Dict) -> Dict:
    msg = (state.get("user_message") or "").lower()
    # Example heuristics: look for engagement verbs
    if any(k in msg for k in ("subscribe", "signup", "register")):
        segment = "engaged_subscriber"
        desc = "Users likely to subscribe or sign up."
        confidence = 0.75
    elif any(k in msg for k in ("demo", "trial", "try")):
        segment = "trial_seekers"
        desc = "Users looking for a demo or trial."
        confidence = 0.7
    else:
        segment = "browsers"
        desc = "Casual browsers with low conversion signals."
        confidence = 0.45

    state.setdefault("candidate_segments", []).append({
        "id": segment,
        "description": desc,
        "confidence": confidence,
        "source": "BEHAVIORAL_SEGMENTATION",
    })

    return state
