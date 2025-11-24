"""Intent segmentation node (explainable template).

Provides an example intent segmentation node that produces a
label, confidence and human-readable justification for downstream use.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from langgraph.runtime import Runtime

from agent.phases.generation.variants import generate_variants
from agent.state import Context, GraphState

logger = logging.getLogger(__name__)


async def generation_node(state: GraphState, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Produce a generation output conditioned on the final segment and context."""
    customer_info = {
        # Core PII identifiers (safe to pass locally, generator handles redaction for LLM)
        "id": state.get("event_metadata", {}).get("user_id"),
        "email": state.get("profile", {}).get("email"),
        "first_name": state.get("profile", {}).get("first_name"),
        "name": state.get("profile", {}).get("name"), 
        
        # Add all other profile attributes for the generator's internal use
        **state.get("profile", {}), 
    }
    # 2. Prepare Segment Info Dictionary
    segment_info = {
        # The primary, prioritized outcome
        "final_segment_label": state.get("final_segment"),
        # Pull details from the raw outputs (assuming they contain the required labels)
        "intent_level": state.get("raw_segment_results", {}).get("intent_segment_output", {}).get("label"), 
        "rfm_label": state.get("raw_segment_results", {}).get("rfm_segment_output", {}).get("label"),
        # If available, also include campaign goal and user message for context
        "campaign_goal": state.get("campaign_goal"),
        "user_message": state.get("user_message"),
        # Add the entire raw segment dicts for maximum context
        **state.get("raw_segment_results", {})
    }
    # 3. Prepare Citations (Retrieved Content)
    citations_data: List[Dict[str, Any]] = state.get("retrieved_content", [])
    
    # 4. Invoke the Robust Generator Agent
    # This single call handles LLM invocation, RAG prompt construction, fallback, and output parsing.
    variants: List[Dict[str, Any]] = generate_variants(
        customer=customer_info, 
        segment=segment_info, 
        citations=citations_data
    )
    # # You could also include the full prompt in the output for debugging
    # return {"generation_output": {"message": msg, "safety": safety, "final_prompt": prompt}}
# 5. Update the GraphState with the generated variants
    # The downstream experimentation_node relies on this field.
    return {
        "message_variants": variants,
        # NOTE: If you need to run an explicit, post-generation safety check 
        # (e.g., using your old safety_agent), you would add it here:
        # "compliance_log": safety_agent.check_safety(variants),
    }