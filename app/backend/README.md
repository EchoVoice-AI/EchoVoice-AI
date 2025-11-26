# New LangGraph Project

[![CI](https://github.com/langchain-ai/new-langgraph-project/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/langchain-ai/new-langgraph-project/actions/workflows/unit-tests.yml)
[![Integration Tests](https://github.com/langchain-ai/new-langgraph-project/actions/workflows/integration-tests.yml/badge.svg)](https://github.com/langchain-ai/new-langgraph-project/actions/workflows/integration-tests.yml)

This template demonstrates a simple application implemented using [LangGraph](https://github.com/langchain-ai/langgraph), designed for showing how to get started with [LangGraph Server](https://langchain-ai.github.io/langgraph/concepts/langgraph_server/#langgraph-server) and using [LangGraph Studio](https://langchain-ai.github.io/langgraph/concepts/langgraph_studio/), a visual debugging IDE.

<div align="center">
  <img src="./static/studio_ui.png" alt="Graph view in LangGraph studio UI" width="75%" />
</div>

The core logic defined in `src/agent/graph.py`, showcases an single-step application that responds with a fixed string and the configuration provided.

You can extend this graph to orchestrate more complex agentic workflows that can be visualized and debugged in LangGraph Studio.

## Getting Started

1. Install dependencies, along with the [LangGraph CLI](https://langchain-ai.github.io/langgraph/concepts/langgraph_cli/), which will be used to run the server.

```bash
cd path/to/your/app
pip install -e . "langgraph-cli[inmem]"
```

2. (Optional) Customize the code and project as needed. Create a `.env` file if you need to use secrets.

```bash
cp .env.example .env
```

If you want to enable LangSmith tracing, add your LangSmith API key to the `.env` file.

```text
# .env
LANGSMITH_API_KEY=lsv2...
```

3. Start the LangGraph Server.

```shell
langgraph dev
```

For more information on getting started with LangGraph Server, [see here](https://langchain-ai.github.io/langgraph/tutorials/langgraph-platform/local-server/).

## How to customize

1. **Define runtime context**: Modify the `Context` class in the `graph.py` file to expose the arguments you want to configure per assistant. For example, in a chatbot application you may want to define a dynamic system prompt or LLM to use. For more information on runtime context in LangGraph, [see here](https://langchain-ai.github.io/langgraph/agents/context/?h=context#static-runtime-context).

2. **Extend the graph**: The core logic of the application is defined in [graph.py](./src/agent/graph.py). You can modify this file to add new nodes, edges, or change the flow of information.

## Development

While iterating on your graph in LangGraph Studio, you can edit past state and rerun your app from previous states to debug specific nodes. Local changes will be automatically applied via hot reload.

Follow-up requests extend the same thread. You can create an entirely new thread, clearing previous history, using the `+` button in the top right.

For more advanced features and examples, refer to the [LangGraph documentation](https://langchain-ai.github.io/langgraph/). These resources can help you adapt this template for your specific use case and build more sophisticated conversational agents.

LangGraph Studio also integrates with [LangSmith](https://smith.langchain.com/) for more in-depth tracing and collaboration with teammates, allowing you to analyze and optimize your chatbot's performance.


## Database setup & migrations

This project supports persisting segment configuration to Postgres (optional). The steps below show how to create a local Postgres database, set the `DATABASE_URL` environment variable in PowerShell, and run Alembic migrations. Replace names and passwords as appropriate for your environment.

1. Activate your Python virtual environment (PowerShell):

```powershell
& .\.venv\Scripts\Activate.ps1
# or adapt to your venv path
```

2. (If needed) install Python dependencies:

```powershell
pip install -r requirements.txt
# or if you use editable install: pip install -e .
```

3. Create a Postgres user and database (run these as a Postgres superuser or via `psql`):

```powershell
# run as the postgres superuser
psql -U postgres -c "CREATE USER echovoice_user WITH PASSWORD 'yiour password';"
psql -U postgres -c "CREATE DATABASE echovoice_db OWNER echovoice_user;"
psql -U postgres -c "GRANT ALL ON SCHEMA public TO echovoice_user;"
```

4. Set the `DATABASE_URL` environment variable in PowerShell (DO NOT prepend `DATABASE_URL=` in the value):

```powershell
$env:DATABASE_URL = 'postgresql+psycopg2://echovoice_user:echovoice_password@localhost:5432/echovoice_db'
```

5. Run Alembic migrations from the `backend` directory. If the `alembic` console entrypoint is not available, run via the venv Python module:

```powershell
# from backend/ directory
python -m alembic -c alembic.ini upgrade head
# or if alembic is on PATH:
alembic -c alembic.ini upgrade head
```

Notes & troubleshooting
- If you see an SQLAlchemy URL parsing error, ensure the env var value is the raw URL string (no extra `DATABASE_URL=` prefix).
- If Alembic fails with `permission denied for schema public`, connect as a superuser and run the `GRANT ALL ON SCHEMA public TO <user>;` command shown above.
- After migrations run, the backend will persist/retrieve segments from Postgres when `DATABASE_URL` is present.

6. Start the FastAPI dev server (run from `backend/`):

```powershell
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

