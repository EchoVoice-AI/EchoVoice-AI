from typing import Dict, Any
from PersonalizeAI.state import GraphState


def winning_variant_selector(state: GraphState) -> Dict[str, Any]:
    performance_data = state.get("predicted_performance", {}) or {}

    best_score = -1.0
    winner_id = None

    for variant_id, metrics in performance_data.items():
        score = metrics.get("predicted_ctr", 0.0) * metrics.get("predicted_lift", 1.0)
        if score > best_score:
            best_score = score
            winner_id = variant_id

    if winner_id:
        print(f"Winning Variant Selected: {winner_id} (Score: {best_score:.4f})")
    else:
        winner_id = next(iter(performance_data.keys()), None)

    return {"winning_variant_id": winner_id}
