# 🚀 EchoVoice — Customer Personalization Orchestrator

EchoVoice is a modular multi‑agent personalization prototype built around a LangGraph workflow. It demonstrates a safety-first, auditable pipeline that converts customer events into grounded, on‑brand message variants (A/B/C), evaluates them, and (optionally) delivers via a mock email service.

This repository is targeted at rapid experimentation and local development. It includes:

- a LangGraph-based orchestrator (`backend/app/graph/langgraph_flow.py`)
- small, testable agent implementations (`backend/agents/`)
- service adapters for vector search and delivery (`backend/services/`)
- a tiny in-memory `MemoryStore` (with optional Redis adapter) under `backend/app/store`
- a React stub for auditability in `frontend/`

---

## Quick Start (Backend)

1. Copy `.env.template` to `.env` and fill any secrets you plan to use (optional for local runs):

```bash
cp .env.template .env
```

2. Create and activate a Python virtual environment, then install dependencies:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Run the API (FastAPI + Uvicorn):

```bash
# from backend/
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. Health check and orchestration endpoint:

```http
GET  http://localhost:8000/health
POST http://localhost:8000/orchestrate

POST body example:
{
  "customer": {
    "id": "U12345",
    "email": "a@example.com",
    "last_event": "payment_plans",
    "properties": {"form_started": "yes"}
  }
}
```

---

## Repository layout (important files)

`EchoVoice-AI/`

- `README.md` — this file
- `ARCHITECTURE.md` — architecture design and flow
- `backend/`
  - `app/main.py` — FastAPI app & CORS setup
  - `app/routers/orchestrator.py` — `/orchestrate` router that invokes the `Orchestrator`
  - `app/graph/langgraph_flow.py` — LangGraph flow definition (segmenter → retriever → generator → safety → hitl → analytics → delivery)
  - `app/graph/orchestrator.py` — lightweight `Orchestrator` wrapper used by the router
  - `app/nodes/*.py` — LangGraph node wrappers (`segmenter_node`, `retriever_node`, `generator_node`, `safety_node`, `analytics_node`, `hitl_node`)
  - `app/store/` — `MemoryStore` and optional `RedisStore` adapters; a `store` singleton is exported
  - `agents/` — agent implementations used by nodes (`segmenter.py`, `retriever.py`, `generator.py`, `safety_gate.py`, `analytics.py`)
  - `services/` — helpers & adapters: `vector_db.py` (FAISS + embeddings), `delivery.py` (mock `send_email_mock`), `logger.py`
- `frontend/` — React audit dashboard stub
- `data/` — sample JSONL corpus and other test fixtures

---

## How the system works (summary)

- The FastAPI router (`app/routers/orchestrator.py`) yields a per-request `Orchestrator` instance.
- `Orchestrator.run_flow` persists a `flow_started` marker, runs the injected `SegmenterNode` for compatibility tests, and then invokes the LangGraph flow (`app/graph/langgraph_flow.py`).
- The LangGraph flow composes small node wrappers that call into the agent modules under `backend/agents/`:
  - `segmenter` → `agents.segmenter.segment_user` produces a full `segment` dict
  - `retriever` → `agents.retriever.retrieve_citations` performs RAG via `services.vector_db.similarity_search` and redacts PII
  - `generator` → `agents.generator.generate_variants` prefers an LLM (Azure/OpenAI) and falls back to templates
  - `safety` → `agents.safety_gate.safety_check_and_filter` filters blocked variants (rule-based)
  - `hitl` → prepares a human-review payload (non-blocking)
  - `analytics` → `agents.analytics.evaluate_variants` produces mock CTRs and picks a winner
  - `delivery` → uses `services.delivery.send_email_mock` to simulate sending

All node outputs are persisted into the `store` for inspection and auditability.

---

## Developer notes

- The `retriever` returns a list of citation dicts with both `text` and `redacted_text`. The generator deliberately uses `redacted_text` when sending context to LLMs.
- `generator` will use Azure OpenAI or OpenAI when environment variables are present; otherwise it falls back to deterministic template generation so flows are testable without secrets.
- `safety_gate.py` currently performs simple rule-based checks (`PROHIBITED_TERMS`). Extend it with model-based classification and explicit human review routing for production.
- `vector_db.py` uses FAISS + embeddings in `services/` and exposes `similarity_search(query, k)` which returns LangChain `Document` objects.

---

## Next steps & suggestions

- Add a small integration test that runs `Orchestrator.run_flow` with `MemoryStore` and mocked LLM responses.
- Add CI to validate the LangGraph flow and safety rule regressions.
- Replace `send_email_mock` with a delivery adapter for real senders (Mail service, Azure Communication Services) behind a configuration flag.

If you'd like, I can now regenerate `ARCHITECTURE.md` to include updated diagrams, or produce agent prompt templates ready for Azure OpenAI. Tell me which you'd like next.
