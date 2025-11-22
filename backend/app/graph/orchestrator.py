"""
Orchestrator placeholder class.

This module provides a minimal `Orchestrator` class with an async
`run_flow` method that now delegates execution to the LangGraph
graph built in `app.graph.langgraph_flow.build_graph`.
"""
from typing import Any, Dict, Optional

from app.store import MemoryStore, store
from app.graph.langgraph_flow import build_graph
from services.logger import get_logger


logger = get_logger("graph.orchestrator")


class Orchestrator:
    """Lightweight orchestrator for flow execution.

    The class is intentionally minimal: it accepts an optional `store`
    and `logger`, persists an initial marker, and returns a stable
    response shape from `run_flow` while delegating the actual flow
    execution to the LangGraph graph.
    """

    def __init__(
        self,
        store_: Optional[MemoryStore] = None,
        logger_=None,
        # kept for backward compatibility, but no longer used directly:
        segmenter=None,
        retriever=None,
        generator=None,
        safety=None,
        hitl=None,
        analytics=None,
    ) -> None:
        # Prefer an explicitly provided store, otherwise fall back to the module-level `store`
        self.store = store_ or store
        self.logger = logger_ or logger

        # Build the LangGraph graph once per orchestrator instance
        self.graph = build_graph()

    def close(self) -> None:
        """Cleanup resources held by the orchestrator or graph.

        This is a best-effort hook. If the graph exposes a `close` or
        `shutdown` method it will be called.
        """
        try:
            close_fn = getattr(self.graph, "close", None) or getattr(
                self.graph, "shutdown", None
            )
            if callable(close_fn):
                close_fn()
        except Exception:
            logger.exception("error closing graph")

    async def run_flow(self, flow_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Run a named flow with the given payload via the LangGraph graph.

        Behavior:
        - Persist a `flow_started` marker keyed by id/email
        - Invoke the LangGraph graph asynchronously with the customer payload
        - Extract key fields from the resulting state and return them
        """
        key = payload.get("id") or payload.get("email") or "anon"

        # Best-effort: mark that the flow started
        try:
            self.store.set(
                f"{key}:flow_started", {"flow": flow_name, "payload": payload}
            )
        except Exception:
            # best-effort: store is optional and should not break execution
            logger.exception("failed to persist flow marker")

        # Invoke the LangGraph graph with the expected input shape
        # The graph is expected to work off `{"customer": payload}`
        self.logger.info("Invoking graph for flow '%s'", flow_name)
        result_state = await self.graph.ainvoke({"customer": payload}) or {}

        # Extract values from the graph state
        segment = result_state.get("segment")
        citations = result_state.get("citations")
        variants = result_state.get("variants")
        safety = result_state.get("safety")
        hitl = result_state.get("hitl")
        analysis = result_state.get("analysis")
        delivery = result_state.get("delivery")

        # Optionally persist key pieces of state for inspection/debugging
        for field_name, value in [
            ("segment", segment),
            ("citations", citations),
            ("variants", variants),
            ("safety", safety),
            ("hitl", hitl),
            ("analysis", analysis),
            ("delivery", delivery),
        ]:
            try:
                self.store.set(f"{key}:{field_name}", value)
            except Exception:
                self.logger.exception("failed to persist %s", field_name)

        response: Dict[str, Any] = {
            "segment": segment,
            "citations": citations,
            "variants": variants,
            "safety": safety,
            "hitl": hitl,
            "analysis": analysis,
            "delivery": delivery,
        }

        self.logger.info("Orchestrator.run_flow completed: %s", flow_name)
        return response


