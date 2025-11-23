Lightweight Swagger runner
=========================

This file documents how to run a lightweight local FastAPI server that exposes the project's OpenAPI/Swagger UI without installing heavy dependencies (FAISS, LangChain, etc.).

What it does
- Creates a tiny FastAPI app that includes the health endpoint and a dummy `/orchestrate` route with the same request model shapes used by the real app. This is intended only for local OpenAPI inspection and development of client code.

Files
- `run_swagger_light.py` — lightweight runner added to the `backend/` folder.

## Run locally (recommended)
1. Change to the `backend/` folder:

```bash
cd backend
```

2. Create a virtual environment and install minimal deps:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip setuptools wheel
./.venv/bin/pip install fastapi uvicorn python-dotenv pydantic
```

3. Start the lightweight server (detached):

```bash
cd backend
nohup ./.venv/bin/python -m uvicorn run_swagger_light:app --app-dir $(pwd) --host 127.0.0.1 --port 8000 > /tmp/evai_uvicorn.log 2>&1 &
echo "server started, logs -> /tmp/evai_uvicorn.log"
```

4. Open Swagger UI in your browser:

    http://127.0.0.1:8000/docs

Or fetch the OpenAPI spec directly:

```bash
curl http://127.0.0.1:8000/openapi.json | jq .
```

Notes and next steps
- The dummy `/orchestrate` endpoint only echoes the parsed payload and does not execute orchestration logic.
- If you want the real endpoints wired up in Swagger you must install the full backend dependencies (see `requirements.txt`) — this will take longer and requires heavy packages such as FAISS.
