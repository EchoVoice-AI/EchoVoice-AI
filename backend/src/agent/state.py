"""Extended GraphState for the LangGraph-based personalization engine.

This schema contains:
- Raw segmentation inputs (campaign goal, user message)
- Behavioral events & system logs
- RFM data
- Profile attributes
- Downstream fields for retrieval, generation, compliance, and experiments
"""

from dataclasses import dataclass
from typing import Any, Dict, List, TypedDict


# ---------- Substructures ----------
class EventMetadata(TypedDict):
    event_id: str
    timestamp: str
    channel: str | None
    session_id: str | None
    user_id: str | None

class BehavioralEvent(TypedDict):
    type: str
    timestamp: str | None
    metadata: Dict[str, Any] | None


class SystemLogs(TypedDict):
    latency_ms: int | None
    backend_error: str | None
    device_type: str | None
    network_strength: str | None


class RFMData(TypedDict):
    recency_days: int | None
    frequency: int | None
    monetary_value: float | None


class UserProfile(TypedDict):
    user_id: str | None
    plan: str | None
    region: str | None
    tenure_days: int | None
    preferences: Dict[str, Any] | None


# ---------- Full GraphState ----------

@dataclass
class GraphState(TypedDict):
    """Shared state for the entire LangGraph pipeline."""

    # --- Event Metadata ---
    event_metadata: EventMetadata

    # --- Phase 1: Raw Segmentation Inputs ---
    campaign_goal: str
    user_message: str | None

    # Additional segmentation signals
    behavioral_events: List[BehavioralEvent]
    system_logs: SystemLogs
    rfm_data: RFMData
    profile: UserProfile
    raw_segment_results: Dict[str, Dict[str, Any]]

    # --- Phase 1 Output: Final Segmentation Result ---
    final_segment: str
    confidence: float
    segment_description: str

    # --- Phase 2: Content Retrieval ---
    context_query: str | None
    retrieved_content: List[Dict[str, str]]

    # --- Phase 3: Message Generation & Compliance ---
    message_variants: List[Dict[str, str]]
    compliance_log: List[Dict[str, Any]]

    # --- Phase 4: Experimentation & Feedback ---
    winning_variant_id: str | None
    predicted_performance: Dict[str, Any]
    feedback_payload: Dict[str, Any]


# ---------- Context Definition (Cloud Config) ----------

class Context(TypedDict):
    """Optional runtime parameters."""
    my_configurable_param: str


__all__ = ["GraphState", "Context"]
