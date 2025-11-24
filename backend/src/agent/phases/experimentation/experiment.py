from typing import Any, Dict

from langgraph.runtime import Runtime

from agent.phases.experimentation.ab_simulator import simulate_ab
from agent.phases.experimentation.feedback_processor import process_feedback
from agent.phases.experimentation.selector import select_variant
from agent.state import Context, GraphState


async def experimentation_node(
    state: GraphState, runtime: Runtime[Context]
) -> Dict[str, Any]:
    """Handle variant assignment, simulates performance, and processes feedback.
    
    to determine the winning variant and update relevant state fields.
    """
    final_segment = state.get("final_segment") if isinstance(state, dict) else "default"
    
    # Assume message_variants holds the outputs from generation_node
    message_variants = state.get("message_variants", []) 
    
    # If variants aren't in the state yet (or are empty), use a default list
    variant_names = [f"Variant_{i}" for i in range(len(message_variants))] or ["A", "B"]
    
    # --- A. Variant Assignment ---
    # Assign the user to a variant (e.g., A/B/C) for this interaction
    assigned_variant = select_variant(
        {"segment": final_segment, "user_id": state.get("event_metadata", {}).get("user_id")}, 
        variant_names
    )
    
    # --- B. Simulated Performance & Winner Selection ---
    # Simulates running an A/B test over the full set of variants
    # Note: This step is usually run offline, but here we simulate instant result/winner calculation.
    variant_map = {name: name for name in variant_names} # Simple map for simulation input
    simulated_results = simulate_ab(variant_map)

    winning_variant = simulated_results.get("winner", assigned_variant)
    predicted_stats = simulated_results.get("stats", {"CTR": 0.05, "conversion": 0.01})
    
    # --- C. Feedback Processing (Placeholder for async data flow) ---
    # Simulates recording and processing telemetry/feedback from prior interactions
    dummy_feedback = {
        "variant": assigned_variant, 
        "result_code": 200, 
        "latency": 350,
        "segment": final_segment
    }
    processed_feedback = process_feedback(dummy_feedback)

    # --- D. Return State Updates ---
    return {
        # 1. Which variant won the (simulated) test?
        "winning_variant_id": winning_variant, 
        
        # 2. What was the predicted outcome?
        "predicted_performance": predicted_stats,
        
        # 3. What feedback was processed?
        "feedback_payload": processed_feedback,
        
        # 4. The variant assigned to the user (used by deployment_node)
        "experiment_assignment": {"variant": assigned_variant} 
    }