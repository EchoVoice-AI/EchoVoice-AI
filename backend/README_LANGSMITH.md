LangSmith monitoring (opt-in)
=================================

This project includes a lightweight, opt-in LangSmith instrumentation wrapper at `backend/services/langsmith_monitor.py`.

Purpose
-------
- Provide safe, non-blocking telemetry hooks for agents (generator, retriever, etc.).
- No-op by default so local dev and CI are unaffected.
- When enabled, the wrapper either forwards to the LangSmith SDK (if installed and configured) or writes local JSON run files under `backend/.langsmith_local_runs/`.

How to enable
-------------
1. Set the environment variable `LANGSMITH_ENABLED=1` or `LANGSMITH_API_KEY=<your_key>`.
2. (Optional) Install the LangSmith SDK in your Python environment: `pip install langsmith`.

Behavior
--------
- If `LANGSMITH_ENABLED` is not present, the wrapper functions (`start_run`, `log_event`, `finish_run`) are no-ops.
- If enabled but the SDK is not installed, the wrapper writes JSON files to `backend/.langsmith_local_runs/` for inspection.
- Instrumented agents: `backend/agents/generator.py` and `backend/agents/retriever.py` call the wrapper at start/finish/error points.

Next steps
----------
1. Review the small changes in `backend/services/langsmith_monitor.py` and the agent instrumentation.
2. Run a smoke test locally (no secrets required):

```bash
# from repo root
backend/.venv/bin/python -c "import sys; sys.path.insert(0,'backend'); from services.langsmith_monitor import LANGSMITH_ENABLED; print('LANGSMITH_ENABLED=', LANGSMITH_ENABLED)"
```

3. To fully integrate with LangSmith UI, set `LANGSMITH_API_KEY` and install the SDK. We can then update `langsmith_monitor.py` to use the SDK client directly.

4. Coordinate with the team on run naming, metadata shape, and whether to prefer a central tracer vs per-agent instrumentation.
# LangSmith monitor (opt-in)

This folder contains a lightweight, opt-in LangSmith monitoring wrapper and example instrumentation for generator and retriever agents.

How it works
- The wrapper is `backend/services/langsmith_monitor.py`.
- By default the wrapper is disabled and is a no-op. To enable set one of:
  - `LANGSMITH_API_KEY` (preferred)
  - `LANGSMITH_ENABLED=1` (for local testing; writes local JSON files)
- When enabled and the `langsmith` SDK is installed, the wrapper can be extended to forward runs to LangSmith.

Local testing
- Without enabling Langsmith, instrumentation will not affect runtime.
- If you want to inspect local runs instead of sending to LangSmith:
  ```bash
  export LANGSMITH_ENABLED=1
  # run your agent (from repo root):
  cd backend
  ./venv/bin/python -c "from services import langsmith_monitor; print(langsmith_monitor.LANGSMITH_ENABLED)"
  # local run files are written to backend/.langsmith_local_runs/
  ```

Next steps
- Optionally wire the wrapper to the real `langsmith` SDK when team is ready.
- Decide a naming convention for run names and metadata, and extend the wrapper to include team-specific fields.

Debug UI (development only)
----------------------------
This repository includes a small developer-only debug UI that helps visualize and
exercise the LangGraph used by the app. The endpoints are intentionally gated so
they are not available in production runs.

Endpoints (use only in local/dev):
- `GET /debug/graph` — returns a compact JSON description of the graph (nodes,
  edges and a Mermaid diagram string).
- `GET /debug/graph/view` — a tiny HTML viewer that fetches `/debug/graph`
  client-side and renders the Mermaid diagram in the browser (avoids server-side
  JS interpolation issues).
- `POST /debug/run` — invokes a local LangGraph smoke run and returns the
  `final_state` JSON. Use this only in safe, local environments.

Enable the debug UI
-------------------
Set the environment variable `ENABLE_DEBUG_UI=1` before starting the backend to
enable these routes. When not set (default) the endpoints return 404.

Example (local):

```bash
export PYTHONPATH=backend
export ENABLE_DEBUG_UI=1
backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8002 --reload
```

CI note
-------
The integration test `backend/tests/test_debug_graph.py` exercises these debug
endpoints and the smoke-run. The test is included in CI so changes to the graph
or debug router will be validated automatically. See `.github/workflows/ci.yml`.

Notes
- The wrapper is intentionally minimal to avoid adding runtime risks. It writes local JSON files when enabled and the SDK is not installed.
LangSmith integration (opt-in)
=================================

This folder contains a lightweight, opt-in wrapper to record agent runs locally
or forward to LangSmith when enabled.

How to enable (local testing)
- By default the monitor is disabled. To enable local JSON recording set:

```bash
export LANGSMITH_ENABLED=1
```

This will create run files under `backend/.langsmith_local_runs/` for each
instrumented agent run.

How to enable real LangSmith (team)
- Install the `langsmith` package into your Python environment.
- Set an API key:

```bash
export LANGSMITH_API_KEY=sk_...your_key...
```

Notes
- The wrapper is intentionally minimal and no-op by default to avoid
  introducing runtime behavior changes. Once enabled, it records run start,
  events, and finish status. The team can later replace or extend the wrapper
  to call the official LangSmith SDK or to normalize metadata.
