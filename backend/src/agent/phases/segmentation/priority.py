"""Priority computation for segmentation outputs."""
from typing import Any, Dict, List

from langgraph.runtime import Runtime

from agent.state import Context, GraphState


# This function is correct as-is, assuming its input List[Dict[str, Any]] 
# contains dictionaries with "score", "segment", and "details" keys.
def prioritize(segments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Prioritize segmentation outputs based on predefined criteria."""
    # Simple highest score picker
    # Note: We'll assume the list items contain 'score', 'segment', and 'details'
    best = max(segments, key=lambda s: s.get("confidence", 0)) # Using 'confidence' from the nodes
    
    # We need to map the fields from the node output to the expected prioritization output
    return {
        "final_segment": best.get("label"), 
        "confidence": best.get("confidence", 0),
        "segment_description": best.get("justification", {})
    }
def priority_router(state: GraphState) -> str:
    """Decides the next phase based on the final prioritized segment.

    Routes critical segments (e.g., high-risk, high-value) to retrieval (RAG)
    and standard segments directly to generation.
    """
    final_segment = state.get("final_segment", "").lower()

    # --- Conditional Logic ---
    # 1. High-Priority / Critical Segments go to Retrieval
    if "churn" in final_segment or "high-value" in final_segment or "fraud" in final_segment:
        return "retrieval_node"  # <-- Needs RAG for specific instructions/context

    # 2. General Segments go straight to Generation
    # This includes 'neutral', 'general', 'clarification', etc.
    return "generation_node"

async def priority_node(state: GraphState, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Merge segmentation outputs and choose the final prioritized segment."""
    # 1. Retrieve the four segments written by the parallel nodes
    # We must use the keys defined in the individual segmentation node returns.
    segment_outputs = [
        state.get("rfm_segment_output"),         # Assuming the RFM node was also updated
        state.get("intent_segment_output"),      # Provided example
        state.get("behavioral_segment_output"),  # Assuming it was updated
        state.get("profile_segment_output"),     # Provided example
    ]
    
    # Filter out None values in case a node failed or returned nothing
    valid_segments = [s for s in segment_outputs if s is not None]

    if not valid_segments:
        return {}
        
    # 2. Prioritize the segments
    # Note: I'm using the local 'prioritize' function defined above
    prioritized = prioritize(valid_segments)
    
    # 3. Write the results back to the GraphState
    # Note: I'm explicitly returning the raw segments in a consolidated field for logging/debugging
    raw_results = {
        "rfm": state.get("rfm_segment_output"),
        "intent": state.get("intent_segment_output"),
        "behavioral": state.get("behavioral_segment_output"),
        "profile": state.get("profile_segment_output"),
    }
    
    return {
        "raw_segment_results": raw_results, # Populate the new GraphState field
        "final_segment": prioritized.get("final_segment"),
        "confidence": prioritized.get("confidence", 0.0),
        "segment_description": prioritized.get("segment_description", ""),
    }