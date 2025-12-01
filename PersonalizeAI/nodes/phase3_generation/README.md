# Phase 3 — Generation & Compliance

This folder contains a small LangGraph-style set of nodes implementing
the Generation & Compliance Phase (Phase 3) of the personalization engine.

Nodes included:

- `ai_message_generator.py` — Generates multiple personalized message
  variants (A/B/C) from `segment_description` and `retrieved_content`.
- `compliance_agent.py` — Evaluates message variants against a simplified
  safety policy and logs results into `compliance_log`.
- `rewrite_decision.py` — Conditional router that returns `END_PHASE_3` or
  `AUTOMATED_REWRITE` depending on compliance outcomes.
- `automated_rewrite.py` — Performs constrained rewrites for non-compliant
  variants and returns updated `message_variants`.

Notes:
- These modules contain deterministic example logic for local testing and
  unit tests. Replace the deterministic parts with LLM calls and stricter
  policy evaluation in production.
- When integrating into your orchestration, ensure `state` is the shared
  GraphState (a dict-like object) and nodes update the state by returning
  dictionaries of updated keys.
