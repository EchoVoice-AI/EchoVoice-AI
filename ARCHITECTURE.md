# EchoVoice Architecture

This document describes the current architecture of the EchoVoice prototype, aligned to the latest code in `backend/app/` and `backend/agents/`.

## High-level overview

EchoVoice implements a LangGraph-driven multi-node workflow. A FastAPI router yields an `Orchestrator` wrapper which invokes a compiled LangGraph `StateGraph` that runs a sequence of small node wrappers. Each node calls a focused agent (pure-Python functions) in `backend/agents/`.

Primary responsibilities:

- Ingest customer events and context via the `/orchestrate` router
- Classify the user (segment)
- Retrieve grounding documents from the vector store (RAG)
- Generate multiple personalized message variants (A/B/C)
- Apply safety/compliance filtering
- Prepare optional human-in-the-loop review metadata
- Run analytics (mock) and select a winner
- Deliver via a mock email service (development)

## Components & mapping to code

- LangGraph workflow / Orchestrator
  - `backend/app/graph/langgraph_flow.py` — defines the flow and node wiring
  - `backend/app/graph/orchestrator.py` — `Orchestrator` wrapper used by the router

- FastAPI and routers
  - `backend/app/main.py` — FastAPI application entry
  - `backend/app/routers/orchestrator.py` — `/orchestrate` endpoint that yields `Orchestrator`

- Node wrappers (LangGraph nodes)
  - `backend/app/nodes/segmenter_node.py`
  - `backend/app/nodes/retriever_node.py`
  - `backend/app/nodes/generator_node.py`
  - `backend/app/nodes/safety_node.py`
  - `backend/app/nodes/hitl_node.py`
  - `backend/app/nodes/analytics_node.py`

- Agents (pure-Python logic)
  - `backend/agents/segmenter.py` — `segment_user(customer) -> segment dict`
  - `backend/agents/retriever.py` — `retrieve_citations(segment_result) -> list[citation dict]` (calls `services.vector_db.similarity_search`)
  - `backend/agents/generator.py` — `generate_variants(customer, segment, citations)` (LLM first, template fallback)
  - `backend/agents/safety_gate.py` — `safety_check_and_filter(variants) -> {safe, blocked}`
  - `backend/agents/analytics.py` — `evaluate_variants(variants, customer)` (mock scoring)

- Services & adapters
  - `backend/services/vector_db.py` — FAISS + embeddings helper exposing `similarity_search(query, k)`
  - `backend/services/delivery.py` — `send_email_mock(...)` used by the delivery node
  - `backend/services/logger.py` — structured logger helper

- Store (transient state)
  - `backend/app/store/memory_store.py` — in-process `MemoryStore`
  - `backend/app/store/redis_store.py` — optional Redis adapter (used if `REDIS_URL` is set)
  - `backend/app/store/__init__.py` — exports a `store` singleton

## Data flow (sequence)

1. FastAPI `/orchestrate` router constructs an `Orchestrator` instance and calls `Orchestrator.run_flow` with `customer` payload.
2. `Orchestrator.run_flow` persists a `flow_started` marker in `store` and invokes the injected `SegmenterNode` (compatibility hook) which runs `agents.segmenter.segment_user` and persists the `segment`.
3. The LangGraph flow (`langgraph_flow.build_graph`) is invoked with initial state `{"customer": payload}`.
4. Node sequence: `segmenter` → `retriever` → `generator` → `safety` → `hitl` → `analytics` → `delivery` → END.
   - `retriever` calls `agents.retriever.retrieve_citations` which builds a query from the `segment` and calls `services.vector_db.similarity_search`. Results are PII-redacted and returned as `citations`.
   - `generator` calls `agents.generator.generate_variants`, which prefers Azure/OpenAI LLMs (if configured) and otherwise uses deterministic templates; it receives `customer`, `segment`, and `citations`.
   - `safety` runs `agents.safety_gate.safety_check_and_filter` to produce `{safe: [...], blocked: [...]}`.
   - `hitl` prepares a non-blocking review payload (review_id) if needed.
   - `analytics` runs `agents.analytics.evaluate_variants` and chooses a winner (mock CTRs).
   - `delivery` uses `services.delivery.send_email_mock` to simulate sending the winning variant.
5. `Orchestrator.run_flow` collects `segment`, `citations`, `variants`, `safety`, `hitl`, `analysis`, and `delivery` from the final graph state, persists them to `store`, and returns a stable response object to the client.

## Safety & compliance

- Current gate: `backend/agents/safety_gate.py` uses `PROHIBITED_TERMS` and a simple substring check to block variants. Blocked variants are annotated with a `reason`.
- Recommendations for production:
  - add model-based classifiers, thresholds, and explainable scores
  - maintain a policy ruleset and tests that assert prohibited classes are blocked
  - require explicit human approval for high-risk categories

## Observability & logging

- Each LangGraph node returns structured outputs; `Orchestrator.run_flow` persists those structures to `store` keyed by customer id/email.
- Use `services.logger` to centralize logs. Consider exporting to a log aggregation service and instrumenting metrics (latency, safety rejections, delivery success).

## Persistence and vector DB

- `services/vector_db.py` builds a FAISS index from `data/*.jsonl` and exposes `similarity_search` for retrieval.
- For local dev, the embedding client falls back to `FakeEmbeddings` so retrieval remains functional (but low-quality) without cloud secrets.

## Delivery

- Delivery is mocked: `services.delivery.send_email_mock` prints and returns a simple `{"status":"sent"}` payload. Replace with a real adapter for production (ACS, SMTP, SES, etc.).

## Extensibility & integration points

- Add alternative retrieval backends by implementing a compatibility layer that mimics `similarity_search(query, k)`.
- Add or replace LangGraph nodes by creating new `app/nodes/*_node.py` wrappers that call into `backend/agents` or external services.
- Integrate a human-review queue (persist HITL jobs in Redis or a DB) and surface them in the `frontend/` audit UI.

## Testing strategy

- Unit tests: each agent in `backend/agents/` should have focused unit tests for edge cases.
- Integration tests: run the LangGraph flow (`app.graph.langgraph_flow.build_graph`) with `MemoryStore` and mock LLM / vector responses.
- Safety regression: add tests that ensure `PROHIBITED_TERMS` and other rules remain enforced.

## Example payloads and outputs

Input (router POST):

```json
{
  "customer": {
    "id": "U123",
    "email": "a@example.com",
    "last_event": "payment_plans",
    "properties": {"form_started": "yes"}
  }
}
```

Example safety output (from `safety_node`):

```json
{
  "safe": [{"id":"A","body":"..."}],
  "blocked": [{"variant": {"id":"B","body":"..."}, "reason": "prohibited_term"}]
}
```


