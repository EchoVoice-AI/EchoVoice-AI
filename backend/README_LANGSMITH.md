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
