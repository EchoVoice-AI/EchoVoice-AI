from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from typing import AsyncGenerator

from services.logger import get_logger
from app.store import MemoryStore, store
from app.graph import Orchestrator
from ..nodes.segmenter_node import SegmenterNode
from ..nodes.retriever_node import RetrieverNode
from ..nodes.generator_node import GeneratorNode
from ..nodes.safety_node import SafetyNode
from ..nodes.analytics_node import AnalyticsNode

router = APIRouter()
logger = get_logger("orchestrator")


def get_store() -> MemoryStore:
    """FastAPI dependency returning the global memory store singleton."""
    return store


def get_segmenter() -> SegmenterNode:
    return SegmenterNode()


def get_retriever() -> RetrieverNode:
    return RetrieverNode()


def get_generator() -> GeneratorNode:
    return GeneratorNode()


def get_safety() -> SafetyNode:
    return SafetyNode()


def get_analytics() -> AnalyticsNode:
    return AnalyticsNode()


async def get_orchestrator(
    store: MemoryStore = Depends(get_store),
    segmenter: SegmenterNode = Depends(get_segmenter),
    retriever: RetrieverNode = Depends(get_retriever),
    generator: GeneratorNode = Depends(get_generator),
    safety: SafetyNode = Depends(get_safety),
    analytics: AnalyticsNode = Depends(get_analytics),
    ) -> AsyncGenerator[Orchestrator, None]:
    """FastAPI dependency returning a per-request Orchestrator instance.

    This constructs an Orchestrator per request using node instances
    provided by DI so tests can override node providers individually.
    """
    orch = Orchestrator(
        store_=store,
        logger_=logger,
        segmenter=segmenter,
        retriever=retriever,
        generator=generator,
        safety=safety,
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
    id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    last_event: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)


class OrchestrateRequest(BaseModel):
    customer: CustomerModel


@router.post("/orchestrate")
async def orchestrate(payload: OrchestrateRequest, orchestrator: Orchestrator = Depends(get_orchestrator)):
    # Use Pydantic v2 model_dump for compatibility with newer versions
    customer = payload.customer.model_dump()
    if not customer:
        raise HTTPException(status_code=400, detail="customer missing")

    # Delegate orchestration to the Orchestrator service
    result = await orchestrator.run_flow("default_personalization", customer)
    return result
