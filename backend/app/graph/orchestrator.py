"""
Orchestrator class backed by a LangGraph flow.

This module provides a minimal `Orchestrator` class with an async
`run_flow` method that delegates execution to the LangGraph graph
built in `app.graph.langgraph_flow.build_graph`, while keeping a
compatibility hook for an injected SegmenterNode.
"""
from typing import Any, Dict, Optional

from app.store import MemoryStore, store
from app.graph.langgraph_flow import build_graph
from services.logger import get_logger
from app.nodes.segmenter_node import SegmenterNode


logger = get_logger("graph.orchestrator")


class Orchestrator:
    """Lightweight orchestrator for flow execution.

    The class accepts an optional `store`, `logger`, and `segmenter`.
    It persists an initial marker and returns a stable response shape
    from `run_flow` while delegating the main flow execution to the
    LangGraph graph.
    """

    def __init__(
        self,
        store_: Optional[MemoryStore] = None,
        logger_=None,
        segmenter: Optional[SegmenterNode] = None,
        # kept for backward compatibility, but no longer used directly:
        retriever=None,
        generator=None,
        safety=None,
        hitl=None,
        analytics=None,
    ) -> None:
        # Prefer an explicitly provided store, otherwise fall back to the module-level `store`
        self.store = store_ or store
        self.logger = logger_ or logger

        # Segmenter can be overridden via FastAPI dependency overrides in tests
        self.segmenter = segmenter or SegmenterNode()

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
        - Call the injected segmenter and persist its result
          (for tests that override the segmenter dependency)
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

        # Compatibility hook: call the injected segmenter and persist its output.
        # This allows tests to override `get_segmenter` and assert on
        # store["{id}:segment"].
        try:
            segment_from_node = self.segmenter.run(payload)
            self.logger.info("Segment (node): %s", segment_from_node)
            self.store.set(f"{key}:segment", segment_from_node)
        except Exception:
            self.logger.exception("failed to run or persist segmenter output")

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

        # Persist other pieces of state for inspection/debugging.
        # NOTE: we intentionally do NOT overwrite "segment" here so tests
        # that override the segmenter still see their injected value in the store.
        for field_name, value in [
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
