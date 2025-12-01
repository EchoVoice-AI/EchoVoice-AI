from typing import Dict, Any
from PersonalizeAI.state import GraphState


def abn_experiment_simulator(state: GraphState) -> Dict[str, Any]:
    """
    Simulates CTR and conversion lift for each compliant variant.
    """
    variants = state.get("message_variants", []) or []
    final_segment = state.get("final_segment", "")

    compliant_ids = {log["variant_id"] for log in state.get("compliance_log", []) if log.get("is_compliant")}
    compliant_variants = [v for v in variants if v.get("id") in compliant_ids]

    simulated_performance: Dict[str, Dict[str, float]] = {}

    for variant in compliant_variants:
        variant_id = variant.get("id")
        if variant_id == "A" and "High Engagement" in final_segment:
            ctr = 0.085
            lift = 1.15
        elif variant_id == "B":
            ctr = 0.062
            lift = 1.05
        else:
            ctr = 0.05
            lift = 1.0

        simulated_performance[variant_id] = {"predicted_ctr": ctr, "predicted_lift": lift}
        print(f"Variant {variant_id} simulated: CTR={ctr:.3f}, Lift={lift:.2f}x")

    return {"predicted_performance": simulated_performance}
