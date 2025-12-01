from typing import Literal
from PersonalizeAI.state import GraphState


def rewrite_decision(state: GraphState) -> Literal["END_PHASE_3", "AUTOMATED_REWRITE"]:
    """
    Inspect `compliance_log` and route to either end the phase or trigger
    the automated rewrite loop when non-compliant variants exist.
    """
    compliance_log = state.get("compliance_log", []) or []

    latest_failures = [log for log in compliance_log if not log.get("is_compliant")]
    non_compliant_variants = {log["variant_id"] for log in latest_failures}

    if non_compliant_variants:
        print(f"Compliance Check: FAIL. {len(non_compliant_variants)} variants need rewriting.")
        return "AUTOMATED_REWRITE"
    else:
        print("Compliance Check: PASS. All variants are approved for experimentation.")
        return "END_PHASE_3"
