"""Orchestrator placeholder class.

This module provides a minimal `Orchestrator` class with an async
`run_flow` method that serves as a placeholder for the full runbook
graph executor implemented in a later issue.
"""
from typing import Any, Dict, Optional

from app.store import MemoryStore, store
from services.logger import get_logger
from app.nodes.segmenter_node import SegmenterNode
from app.nodes.retriever_node import RetrieverNode
from app.nodes.generator_node import GeneratorNode
from app.nodes.safety_node import SafetyNode
from app.nodes.analytics_node import AnalyticsNode
from services.delivery import send_email_mock


logger = get_logger("graph.orchestrator")


class Orchestrator:
    """Lightweight orchestrator for flow execution.

    The class is intentionally minimal: it accepts an optional `store`
    and `logger`, persists an initial marker, and returns a stable
    response shape from `run_flow` so integration tests can exercise
    it without depending on execution details.
    """

    def __init__(
        self,
        store_: Optional[MemoryStore] = None,
        logger_=None,
        segmenter: Optional[SegmenterNode] = None,
        retriever: Optional[RetrieverNode] = None,
        generator: Optional[GeneratorNode] = None,
        safety: Optional[SafetyNode] = None,
        analytics: Optional[AnalyticsNode] = None,
    ) -> None:
        # prefer an explicitly provided store, otherwise fall back to the module-level `store`
        self.store = store_ or store
        self.logger = logger_ or logger
        # Use provided node instances or create defaults
        self.segmenter = segmenter or SegmenterNode()
        self.retriever = retriever or RetrieverNode()
        self.generator = generator or GeneratorNode()
        self.safety = safety or SafetyNode()
        self.analytics = analytics or AnalyticsNode()

    def close(self) -> None:
        """Cleanup resources held by the orchestrator or nodes.

        This is a best-effort hook. If nodes expose a `close` or
        `shutdown` method it will be called.
        """
        for node in (self.segmenter, self.retriever, self.generator, self.safety, self.analytics):
            try:
                close_fn = getattr(node, "close", None) or getattr(node, "shutdown", None)
                if callable(close_fn):
                    close_fn()
            except Exception:
                logger.exception("error closing node %s", type(node).__name__)

    async def run_flow(self, flow_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Run a named flow with the given payload.

        Placeholder behavior:
        - Persist a `flow_started` marker keyed by id/email
        - Log an informational message
        - Return a stable dictionary describing the run
        """
        key = payload.get("id") or payload.get("email") or "anon"
        try:
            # persist minimal marker for audit/inspection
            self.store.set(f"{key}:flow_started", {"flow": flow_name, "payload": payload})
        except Exception:
            # best-effort: store is optional and should not break placeholder
            logger.exception("failed to persist flow marker")

        # 1. Segmentation
        segment = self.segmenter.run(payload)
        self.logger.info(f"Segment: {segment}")
        try:
            self.store.set(f"{key}:segment", segment)
        except Exception:
            self.logger.exception("failed to persist segment")

        # 2. Retrieval
        citations = self.retriever.run(payload)
        self.logger.info(f"Citations: {citations}")
        try:
            self.store.set(f"{key}:citations", citations)
        except Exception:
            self.logger.exception("failed to persist citations")

        # 3. Generation
        variants = self.generator.run({"customer": payload, "segment": segment, "citations": citations})
        self.logger.info(f"Generated {len(variants) if variants else 0} variants")
        try:
            self.store.set(f"{key}:variants", variants)
        except Exception:
            self.logger.exception("failed to persist variants")

        # 4. Safety checks
        safety_result = self.safety.run(variants)
        safe_count = len(safety_result.get("safe", [])) if isinstance(safety_result, dict) else 0
        blocked_count = len(safety_result.get("blocked", [])) if isinstance(safety_result, dict) else 0
        self.logger.info(f"Safety safe={safe_count} blocked={blocked_count}")

        # 5. Analytics / choose winner
        analysis = self.analytics.run({"variants": safety_result.get("safe", []), "customer": payload}) if isinstance(safety_result, dict) else None
        winner = analysis.get("winner") if isinstance(analysis, dict) and analysis else None
        try:
            self.store.set(f"{key}:analysis", analysis)
            if winner:
                self.store.set(f"{key}:winner", winner)
        except Exception:
            self.logger.exception("failed to persist analysis/winner")

        # 6. Delivery (mock)
        delivery_result = None
        if winner and isinstance(safety_result, dict):
            variant = next((v for v in safety_result.get("safe", []) if v.get("id") == winner.get("variant_id")), None)
            if variant:
                delivery_result = send_email_mock(payload.get("email"), variant.get("subject"), variant.get("body"))

        response = {
            "segment": segment,
            "citations": citations,
            "variants": variants,
            "safety": safety_result,
            "analysis": analysis,
            "delivery": delivery_result,
        }

        self.logger.info("Orchestrator.run_flow completed: %s", flow_name)
        return response
