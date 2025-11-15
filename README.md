# EchoVoice: Customer Personalization Orchestrator 

**Project Title:** `EchoVoice: Customer Personalization Orchestrator`

**Challenge Solved:** Compliant, on-brand personalization and A/B/n experimentation in a regulated domain.

This repository contains a scaffold for "EchoVoice-AI" — a Multi-Agent AI Personalization Platform (orchestrator + agents + frontend stub).

Quick start (backend):

1. Copy `.env.template` to `.env` and fill API keys.
2. Create a Python virtualenv and install dependencies:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Run the backend orchestrator (development):

```bash
cd backend
# Install dependencies first (see requirements.txt)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then POST an event to `http://localhost:8000/orchestrate` with JSON payload to simulate the pipeline.

Repository layout (scaffold):

```
EchoVoice-AI/
├── README.md
├── requirements.txt
├── package.json
├── .env.template
├── data/
├── frontend/
└── backend/
```

## Architecture

This repo contains a small LangGraph-style Agent Team orchestration for local prototyping.

- `agents/` — specialized agents (segmenter, retriever, generator, safety gate, delivery, analytics).
- `data/` — local mock content for RAG and mock customer events.
- `main.py` — FastAPI server and orchestrator glue.
- `Dockerfile` — optional container for deployment.
  
