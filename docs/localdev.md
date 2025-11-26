# 🚀 **EchoVoice: Customer Personalization Orchestrator** : Local development of chat app

After deploying the app to Azure, you may want to continue development locally. This guide explains how to run the app locally, including hot reloading and debugging.

- [🚀 **EchoVoice: Customer Personalization Orchestrator** : Local development of chat app](#-echovoice-customer-personalization-orchestrator--local-development-of-chat-app)
  - [Running development server from the command line](#running-development-server-from-the-command-line)
  - [Hot reloading frontend and backend files](#hot-reloading-frontend-and-backend-files)
  - [Using VS Code "Development" task](#using-vs-code-development-task)
  - [Using Copilot Chat Debug Mode](#using-copilot-chat-debug-mode)
  - [Using VS Code "Run and Debug"](#using-vs-code-run-and-debug)
  - [Using a local OpenAI-compatible API](#using-a-local-openai-compatible-api)
    - [Using Ollama server](#using-ollama-server)
    - [Using llamafile server](#using-llamafile-server)

## Running development server from the command line

You can only run locally **after** having successfully run the `azd up` command. If you haven't yet, follow the steps in [Azure deployment](../README.md#azure-deployment) above.

1. Run `azd auth login`
2. Start the servers locally (activate your venv first and run each command from the workspace root):

  Windows (PowerShell):

  ```powershell
  # activate venv then start backend
  & .\.venv\Scripts\Activate.ps1
  Set-Location backend
  python -m uvicorn api.main:app --reload --port 8000
  ```

  Linux/Mac:

  ```bash
  # activate venv then start backend
  source .venv/bin/activate
  cd backend
  python -m uvicorn api.main:app --reload --port 8000
  ```

  VS Code: Run the "VS Code Task: Start App" task or use the "Development" task described below.

## Hot reloading frontend and backend files

When you run `./start.ps1` or `./start.sh`, the backend files will be watched and reloaded automatically. However, the frontend files will not be watched and reloaded automatically.

To enable hot reloading of frontend files, open a new terminal and navigate to the frontend directory:

```powershell
Set-Location frontend
```

Then run the Next.js dev server on port `8082`:

```powershell
npm run dev -- -p 8082
```

You should see something like:

```text
ready - started server on http://localhost:8082
```

Navigate to the URL shown in the terminal (for example, `http://localhost:8082/`). This Next.js dev server will watch and reload frontend files. Backend requests should be routed to the Python server on port `8000`.

Then, whenever you make changes to frontend files, the changes will be automatically reloaded, without any browser refresh needed.

Alternatively, you can start both servers with hot reloading by using the VS Code "Development" task. See [Using VS Code "Development" task](#using-vs-code-development-task).

## Using VS Code "Development" task

If you prefer VS Code tasks for hot reloading both servers at once, use the "Development" task defined in `.vscode/tasks.json`.

How to run it:

- Run Build Task (Shift+Cmd+B) to start the default build task, which is "Development".
- Or open the Command Palette (Shift+Cmd+P) and run: "Tasks: Run Task" -> "Development".

What it does:

- Starts two background tasks in dedicated panels:
  - "Frontend: npm run dev" from `frontend` (Next.js dev server on port `8082`)
  - "Backend: uvicorn run" from `backend` (Uvicorn/FastAPI on port `8000`)

Readiness indicators:

- Frontend is ready when Next.js prints a ready message and the Local URL, for example: `http://localhost:8082/`.
- Backend is ready when Uvicorn prints a startup message such as: `Uvicorn running on http://127.0.0.1:8000` or `Application startup complete`.

Tips:

- To stop both, run: "Tasks: Terminate Task" and pick the running tasks.
- If watchers stall, terminate and run "Development" again.
- Frontend changes apply via HMR; backend Python changes auto-reload. No manual restart needed.

## Using Copilot Chat Debug Mode

You can use GitHub Copilot Chat with a custom "debug" mode to streamline troubleshooting in this repo.

Prerequisites:

- VS Code 1.101+ (custom chat modes are in preview)
- Access to GitHub Copilot and Copilot Chat
- Playwright MCP server and GitHub MCP server (optional)

To learn more about the chat modes feature, read [VS Code docs for Chat modes](https://code.visualstudio.com/docs/copilot/chat/chat-modes).

To use the debug mode:

- Open the Chat view.
- Use the chat mode dropdown at the top of the Chat view to select the "debug" mode.
- Start chatting in that mode; the instructions and tools from the repo file will be applied automatically.
- The mode will use the tasks from .vscode/tasks.json to run the frontend and backend server, and should be able to read any errors in the output.
- The mode may also use tools from the Playwright MCP server and GitHub MCP server, if those servers are installed in your VS Code.

Notably, this mode will not actually use a breakpoint-based debugger. Read on to learn how to use breakpoints while debugging the Python code.

## Using VS Code "Run and Debug"

This project includes configurations defined in `.vscode/launch.json` that allow you to run and debug the app directly from VS Code:

- "Backend (Python)": Starts the Python backend server, defaulting to port 8000.
- "Frontend": Starts the frontend server using Next.js, typically at port 8082.
- "Frontend & Backend": A compound configuration that starts both the frontend and backend servers.

When you run these configurations, you can set breakpoints in your code and debug as you would in a normal VS Code debugging session.

## Using a local OpenAI-compatible API

You may want to save costs by developing against a local LLM server, such as
[llamafile](https://github.com/Mozilla-Ocho/llamafile/). Note that a local LLM
will generally be slower and not as sophisticated.

Once the local LLM server is running and serving an OpenAI-compatible endpoint, set these environment variables:

```shell
azd env set USE_VECTORS false
azd env set OPENAI_HOST local
azd env set OPENAI_BASE_URL <your local endpoint>
azd env set AZURE_OPENAI_CHATGPT_MODEL local-model-name
```

Then restart the local development server.
You should now be able to use the "Ask" tab.

⚠️ Limitations:

- The "Chat" tab will only work if the local language model supports function calling.
- Your search mode must be text only (no vectors), since the search index is only populated with OpenAI-generated embeddings, and the local OpenAI host can't generate those.
- The conversation history will be truncated using the GPT tokenizers, which may not be the same as the local model's tokenizer, so if you have a long conversation, you may end up with token limit errors.

> [!NOTE]
> You must set `OPENAI_HOST` back to a non-local value ("azure", "azure_custom", or "openai")
> before running `azd up` or `azd provision`, since the deployed backend can't access your local server.

### Using Ollama server

For example, to point at a local Ollama server running the `llama3.1:8b` model:

```shell
azd env set OPENAI_HOST local
azd env set OPENAI_BASE_URL http://localhost:11434/v1
azd env set AZURE_OPENAI_CHATGPT_MODEL llama3.1:8b
azd env set USE_VECTORS false
```

If you're running the app inside a VS Code Dev Container, use this local URL instead:

```shell
azd env set OPENAI_BASE_URL http://host.docker.internal:11434/v1
```

### Using llamafile server

To point at a local llamafile server running on its default port:

```shell
azd env set OPENAI_HOST local
azd env set OPENAI_BASE_URL http://localhost:8080/v1
azd env set USE_VECTORS false
```

Llamafile does *not* require a model name to be specified.

If you're running the app inside a VS Code Dev Container, use this local URL instead:

```shell
azd env set OPENAI_BASE_URL http://host.docker.internal:8080/v1
```
