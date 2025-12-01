# PersonalizeAI — LangGraph-style orchestration package

This package contains lightweight nodes and orchestration helpers for an
End-to-End AI Personalization Engine described across four phases:

- Phase 1: Segmentation (not included in detail here)
- Phase 2: Content Retrieval (Corrective RAG loop)
- Phase 3: Generation & Compliance (Mandatory Safety Loop)
- Phase 4: Experimentation & Feedback (Dual Exit)

## Contents

--------

- `nodes/phase2_retrieval/` — Phase 2 retrieval and self-correction nodes.
- `nodes/phase3_generation/` — Generator, compliance, rewrite, and helpers.
- `nodes/phase4_experimentation/` — Experiment simulator, winner selector, deployment router, and feedback processor.
- `utils/response_cleaner.py` — helpers to extract JSON from LLM outputs and validate them.
- `orchestrator.py` — simple async runner that wires Phase 3 → Phase 4 using the nodes above.

## Quickstart

1. Ensure repository root is on `PYTHONPATH` or run from repo root so `PersonalizeAI` is importable.
2. Create a `state` dict with at least:

```python
state = {
    "segment_description": "High value shoppers",
    "campaign_goal": "Reduce churn",
    "retrieved_content": [{"text": "Fact 1", "source_id": "doc1"}],
}
```

Run the orchestrator (example):

```python
import asyncio
from PersonalizeAI.orchestrator import run_full_pipeline

state = {...}
result = asyncio.run(run_full_pipeline(state))
print(result["winning_variant_id"])  # chosen variant
print(result.get("feedback_payload"))
```

- Nodes attempt to use an `openai_client` and `prompty_manager` when provided via function args; otherwise they fall back to deterministic logic for local testing.
- The orchestrator is defensive and will not fail hard if optional nodes or clients are missing — it will instead use available data and fallbacks.
- The project includes tests under `tests/` demonstrating Phase 2 self-correction and a Phase 3→4 integration test that mocks the OpenAI client.

## Security & Compliance

- The `compliance_agent` and `automated_rewrite` nodes implement a mandatory safety loop: messages must pass the compliance check before being sent to deployment.
- All compliance checks and rewrites are appended to `state["compliance_log"]` and the feedback payload is recorded in `state["feedback_payload"]` for auditability.

## License & Contribution

This code is intended as an internal scaffold/example. Adapt prompts, validators, and LLM usage for your production security and data governance needs.
