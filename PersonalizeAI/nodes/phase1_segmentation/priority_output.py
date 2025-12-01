"""Selects the highest-confidence candidate segment and writes final fields.

Exposes `run(state)` which sets `final_segment`, `confidence`, and `segment_description`.
"""
from typing import Dict, Any


def run(state: Dict[str, Any]) -> Dict[str, Any]:
    candidates = state.get("candidate_segments") or []
    if not candidates:
        # fallback default
        state["final_segment"] = "unknown"
        state["confidence"] = 0.0
        state["segment_description"] = "No candidate segments generated."
        return state

    # pick highest confidence
    best = max(candidates, key=lambda c: c.get("confidence", 0))
    state["final_segment"] = best.get("id")
    state["confidence"] = best.get("confidence")
    state["segment_description"] = best.get("description")
    state["final_segment_source"] = best.get("source")
    return state
