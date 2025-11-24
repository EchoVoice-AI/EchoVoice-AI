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
from app.nodes.retriever_node import RetrieverNode
from app.nodes.generator_node import GeneratorNode
from app.nodes.safety_node import SafetyNode
from app.nodes.hitl_node import HITLNode
from app.nodes.analytics_node import AnalyticsNode
from services.delivery import send_email_mock


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
        retriever: Optional[RetrieverNode] = None,
        generator: Optional[GeneratorNode] = None,
        safety: Optional[SafetyNode] = None,
        hitl: Optional[HITLNode] = None,
        analytics: Optional[AnalyticsNode] = None,
    ) -> None:
        # Prefer an explicitly provided store, otherwise fall back to the module-level `store`
        self.store = store_ or store
        self.logger = logger_ or logger

        # Segmenter can be overridden via FastAPI dependency overrides in tests
        self.segmenter = segmenter or SegmenterNode()
        self.retriever = retriever or RetrieverNode()
        self.generator = generator or GeneratorNode()
        self.safety = safety or SafetyNode()
        self.hitl = hitl or HITLNode() 
        self.analytics = analytics or AnalyticsNode()

    def close(self) -> None:
        """Cleanup resources held by the orchestrator or graph.

        This is a best-effort hook. If the graph exposes a `close` or
        `shutdown` method it will be called.
        """
        for node in (self.segmenter, self.retriever, self.generator, self.safety,self.hitl, self.analytics):
            try:
                close_fn = getattr(node, "close", None) or getattr(node, "shutdown", None)
                if callable(close_fn):
                    close_fn()
            except Exception:
                logger.exception("error closing node %s", type(node).__name__)

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
            self.logger.exception("failed to persist variants")

        # Build and invoke the LangGraph flow to get a final state dict.
        try:
            graph = build_graph()
            final_state = graph.invoke({"customer": payload})
        except Exception:
            self.logger.exception("failed to invoke LangGraph flow")
            final_state = {}

        # Extract expected fields from the final state with safe fallbacks.
        segment = final_state.get("segment")
        citations = final_state.get("citations")
        variants = final_state.get("variants")
        safety_result = final_state.get("safety") or {}
        hitl_result = final_state.get("hitl")
        analysis = final_state.get("analysis")
        delivery_result = final_state.get("delivery")

        # Log safety summary if present
        if isinstance(safety_result, dict):
            safe_count = len(safety_result.get("safe", []))
            blocked_count = len(safety_result.get("blocked", []))
            self.logger.info(f"Safety safe={safe_count} blocked={blocked_count}")

        # Persist transient results (best-effort)
        try:
            if segment is not None:
                # Allow an injected/overridden segmenter (useful in tests)
                try:
                    segment_from_node = self.segmenter.run(payload)
                    segment = segment_from_node
                except Exception:
                    # Fall back to the segment computed by the graph
                    pass
                self.store.set(f"{key}:segment", segment)
            if citations is not None:
                self.store.set(f"{key}:citations", citations)
            if variants is not None:
                self.store.set(f"{key}:variants", variants)
            if hitl_result is not None:
                self.store.set(f"{key}:hitl", hitl_result)
            if analysis is not None:
                self.store.set(f"{key}:analysis", analysis)
        except Exception:
            self.logger.exception("failed to persist transient state")

        response = {
            "segment": segment,
            "citations": citations,
            "variants": variants,
            "safety": safety_result,
            "hitl": hitl_result,
            "analysis": analysis,
            "delivery": delivery_result,
        }

        self.logger.info("Orchestrator.run_flow completed: %s", flow_name)
        return response
