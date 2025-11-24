"""Pydantic models for API request and response payloads.

The models are narrow and intentionally simple: they reflect the fields
the frontend will read and update for segments and lightweight graph
operations.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Segment(BaseModel):
    """A segment configuration item returned to the frontend.

    Attributes:
        id: Unique identifier for the segment (string).
        name: Human-friendly name.
        enabled: Whether this segment is active.
        priority: Numeric priority used by the priority node.
        metadata: Arbitrary JSON metadata attached to the segment.
    """

    id: str
    name: str
    enabled: bool = True
    priority: float = Field(1.0, ge=0.0)
    metadata: Dict[str, Any] = {}


class SegmentUpdate(BaseModel):
    """Partial update payload for a segment.

    Any field may be omitted; only provided fields are applied.
    """

    enabled: Optional[bool]
    priority: Optional[float]
    metadata: Optional[Dict[str, Any]]


class GraphSummary(BaseModel):
    """A minimal representation of the composed agent graph.

    Contains only a name and a list of node identifiers for the UI.
    """

    name: str
    nodes: List[str]


class ValidationResult(BaseModel):
    """Result returned by running lightweight graph validation."""

    valid: bool
    errors: List[str] = []
