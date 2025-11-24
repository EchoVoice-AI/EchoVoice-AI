"""Shared state structures for segmentation phase."""
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class SegmentationState:
    """Shared state for the segmentation phase.

    Attributes:
        final_segment: The final selected segment text.
        confidence: Confidence score associated with the final segment.
        segment_description: A brief human-readable description of the segment.
        raw_segments: A mapping of raw segment identifiers to their data and metadata.
    """
    final_segment: str = ""
    confidence: float = 0.0
    segment_description: str = ""
    raw_segments: Dict[str, Any] = field(default_factory=dict)
