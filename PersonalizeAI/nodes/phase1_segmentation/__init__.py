"""Phase 1 segmentation nodes package.

Exports the goal_router and basic segmenter modules.
"""
from . import goal_router  # simple router

__all__ = [
    "goal_router",
    "rfm_segmenter",
    "intent_segmenter",
    "behavioral_segmenter",
    "profile_segmenter",
    "priority_output",
]
