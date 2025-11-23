"""Lightweight deterministic goal router for segmentation."""
from typing import Dict, Any


def route_goal(message: Dict[str, Any]) -> str:
    """Simple heuristic router: returns segment type key."""
    text = message.get("text", "").lower()
    if any(k in text for k in ["buy", "price", "purchase"]):
        return "rfm"
    if any(k in text for k in ["how", "what", "why", "help"]):
        return "intent"
    if any(k in text for k in ["slow", "frustrated", "angry"]):
        return "behavioral"
    return "profile"
