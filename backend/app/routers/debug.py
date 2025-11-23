from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
import os
from typing import Dict, Any

router = APIRouter(prefix="/debug", tags=["debug"])


def _debug_enabled() -> bool:
    return os.getenv("ENABLE_DEBUG_UI", "false").lower() == "1"


@router.get("/graph")
def get_graph_description() -> Dict[str, Any]:
    """Return a simple JSON description of the LangGraph used by the app.

    This endpoint is intentionally tiny and only enabled when ENABLE_DEBUG_UI=1.
    """
    if not _debug_enabled():
        raise HTTPException(status_code=404, detail="debug UI not enabled")

    # Maintain a small in-code description so this endpoint doesn't need to import
    # the full graph at module import time.
    nodes = [
        "segmenter",
        "retriever",
        "generator",
        "safety",
        "hitl",
        "analytics",
        "delivery",
    ]
    edges = [
        ["segmenter", "retriever"],
        ["retriever", "generator"],
        ["generator", "safety"],
        ["safety", "hitl"],
        ["hitl", "analytics"],
        ["analytics", "delivery"],
    ]

    mermaid = "graph LR\n"
    for a, b in edges:
        mermaid += f"    {a}-->{b}\n"
    mermaid += "    delivery-->END\n"

    return {"nodes": nodes, "edges": edges, "mermaid": mermaid}


@router.get("/graph/view", response_class=HTMLResponse)
def view_graph() -> HTMLResponse:
        """Return a small HTML page that renders the Mermaid diagram for the graph.

        This is gated by ENABLE_DEBUG_UI and intended for local development only.
        """
        if not _debug_enabled():
                raise HTTPException(status_code=404, detail="debug UI not enabled")

        # Serve a small HTML page that client-side fetches /debug/graph and
        # renders the Mermaid diagram. Doing the fetch/render in the browser
        # avoids any server-side string interpolation or brace-escaping issues.
        html = (
            """
        <!doctype html>
        <html>
        <head>
            <meta charset="utf-8" />
            <title>LangGraph - Debug Graph</title>
            <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
            <style>
                body{font-family:Arial,Helvetica,sans-serif;margin:20px}
                .mermaid{background:#f8f8f8;padding:12px;border-radius:6px}
            </style>
        </head>
        <body>
            <h2>LangGraph - Debug Graph</h2>
            <div id="diagram" class="mermaid">Loading...</div>

            <script>
            // Fetch the graph JSON from the debug endpoint and render the mermaid
            // text into the diagram container. This keeps all brace-heavy
            // JavaScript client-side and avoids server-side interpolation.
            (async function(){
                try{
                    const resp = await fetch('/debug/graph');
                    if(!resp.ok){
                        document.getElementById('diagram').innerText = 'Failed to load graph: ' + resp.status;
                        return;
                    }
                    const data = await resp.json();
                    const mermaidText = data.mermaid || 'graph LR\n    ERROR[No mermaid available]';
                    const container = document.getElementById('diagram');
                    container.textContent = mermaidText;
                    // Initialize mermaid and render
                    if(window.mermaid){
                        window.mermaid.initialize({ startOnLoad: false });
                        // mermaid runs automatically on elements with class 'mermaid'
                        window.mermaid.init(undefined, container);
                    } else {
                        // Fallback if mermaid failed to load
                        container.textContent = mermaidText + '\n\n(Note: mermaid failed to load)';
                    }
                }catch(err){
                    document.getElementById('diagram').innerText = 'Error fetching graph: ' + String(err);
                }
            })();
            </script>
        </body>
        </html>
        """
        )

        return HTMLResponse(content=html, status_code=200)


@router.post("/run")
async def run_graph(request: Request) -> Dict[str, Any]:
    """Invoke the LangGraph flow with an optional customer payload and return final state.

    Body (optional): JSON object with a `customer` key. If omitted a default test customer is used.
    """
    if not _debug_enabled():
        raise HTTPException(status_code=404, detail="debug UI not enabled")

    payload = None
    try:
        # Await the Request.json coroutine in async endpoints to avoid
        # "coroutine was never awaited" warnings.
        payload = await request.json()  # type: ignore[attr-defined]
    except Exception:
        # If body is not parseable or empty, we'll use default
        payload = None

    # Import and run lazily to avoid heavy imports at module import time
    from app.graph.langgraph_flow import build_graph

    graph = build_graph()

    if payload and isinstance(payload, dict) and payload.get("customer"):
        initial_state = {"customer": payload.get("customer")}
    else:
        initial_state = {
            "customer": {
                "id": "U_TEST",
                "email": "test@example.com",
                "last_event": "payment_plans",
                "properties": {"form_started": "yes", "scheduled": "no", "attended": "no"},
            }
        }

    final_state = graph.invoke(initial_state)

    return final_state
