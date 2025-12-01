from typing import Dict, Any
from PersonalizeAI.state import GraphState
from datetime import datetime, timezone


def feedback_processor(state: GraphState) -> str:
    payload = {
        "run_id": state.get("run_id", "run-unknown"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "campaign_goal": state.get("campaign_goal"),
        "final_segment": state.get("final_segment"),
        "segment_description": state.get("segment_description"),
        "winning_variant_id": state.get("winning_variant_id"),
        "predicted_metrics": state.get("predicted_performance", {}).get(state.get("winning_variant_id")),
        "citation_sources": [c.get("source_id") for c in state.get("retrieved_content", []) if c.get("source_id")],
        "compliance_summary": [log for log in state.get("compliance_log", []) if not log.get("is_compliant")],
    }

    state["feedback_payload"] = payload

    print("--- Feedback Payload Generated ---")
    print(f"Feedback prepared for learning loop: {payload.get('final_segment')} -> {payload.get('winning_variant_id')}")

    return "END"
