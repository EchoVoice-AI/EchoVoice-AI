from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Segment(BaseModel):
    id: str
    name: str
    enabled: bool = True
    priority: float = Field(1.0, ge=0.0)
    metadata: Dict[str, Any] = {}


class SegmentUpdate(BaseModel):
    enabled: Optional[bool]
    priority: Optional[float]
    metadata: Optional[Dict[str, Any]]


class GraphSummary(BaseModel):
    name: str
    nodes: List[str]


class ValidationResult(BaseModel):
    valid: bool
    errors: List[str] = []
