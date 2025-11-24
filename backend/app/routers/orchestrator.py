from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, AsyncGenerator

from services.logger import get_logger
from app.store import MemoryStore, store
from app.graph import Orchestrator
from app.nodes.segmenter_node import SegmenterNode
from app.nodes.retriever_node import RetrieverNode
from app.nodes.generator_node import GeneratorNode
from app.nodes.safety_node import SafetyNode
from app.nodes.hitl_node import HITLNode
from app.nodes.analytics_node import AnalyticsNode

router = APIRouter()
logger = get_logger("orchestrator")


def get_store() -> MemoryStore:
    """Return the global in-memory store singleton."""
    return store
def get_segmenter() -> SegmenterNode:
    """Default segmenter provider (can be overridden in tests)."""
    return SegmenterNode()


def get_retriever() -> RetrieverNode:
    return RetrieverNode()


def get_generator() -> GeneratorNode:
    return GeneratorNode()


def get_safety() -> SafetyNode:
    return SafetyNode()
def get_hitl() -> HITLNode:
    return HITLNode()


def get_analytics() -> AnalyticsNode:
    return AnalyticsNode()


async def get_orchestrator(
    store: MemoryStore = Depends(get_store),
    segmenter: SegmenterNode = Depends(get_segmenter),
    retriever: RetrieverNode = Depends(get_retriever),
    generator: GeneratorNode = Depends(get_generator),
    safety: SafetyNode = Depends(get_safety),
    hitl: HITLNode = Depends(get_hitl),
    analytics: AnalyticsNode = Depends(get_analytics),
    ) -> AsyncGenerator[Orchestrator, None]:
    """FastAPI dependency returning a per-request Orchestrator instance.

    The Orchestrator delegates flow execution to the LangGraph graph.
    We ensure resources are cleaned up at the end of the request.
    """
    orch = Orchestrator(
        store_=store,
        logger_=logger,
        segmenter=segmenter,
        retriever=retriever,
        generator=generator,
        safety=safety,
        hitl=hitl,
        analytics=analytics,
    )
    try:
        yield orch
    finally:
        try:
            orch.close()
        except Exception:
            logger.exception("error closing orchestrator")


class CustomerModel(BaseModel):
    id: Optional[str] = Field(None, example="U001")
    name: Optional[str] = Field(None, example="Selvi")
    email: Optional[str] = Field(None, example="a@example.com")
    last_event: Optional[str] = Field(None, example="payment_plans")
    properties: Dict[str, Any] = Field(
        default_factory=dict,
        example={
            "form_started": "yes",
            "scheduled": "no",
            "attended": "no",
        },
    )


class OrchestrateRequest(BaseModel):
    customer: CustomerModel


@router.post("/orchestrate")
async def orchestrate(
    payload: OrchestrateRequest,
    orchestrator: Orchestrator = Depends(get_orchestrator),
):
    """Run the personalization flow for a given customer."""
    customer = payload.customer.model_dump()
    if not customer:
        raise HTTPException(status_code=400, detail="customer missing")

    result = await orchestrator.run_flow("default_personalization", customer)
    return result
