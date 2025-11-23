"""Shared state structures for segmentation phase"""
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class SegmentationState:
    final_segment: str = ""
    confidence: float = 0.0
    segment_description: str = ""
    raw_segments: Dict[str, Any] = field(default_factory=dict)
