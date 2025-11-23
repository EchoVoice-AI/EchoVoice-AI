"""Priority computation for segmentation outputs"""
from typing import Dict, Any, List


def prioritize(segments: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Simple highest score picker
    best = max(segments, key=lambda s: s.get("score", 0))
    return {
        "final_segment": best.get("segment"),
        "confidence": best.get("score", 0),
        "segment_description": best.get("details", {})
    }
