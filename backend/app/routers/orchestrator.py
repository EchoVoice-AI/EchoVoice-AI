from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, AsyncGenerator

from services.logger import get_logger
from app.store import MemoryStore, store
from app.graph import Orchestrator
from app.nodes.segmenter_node import SegmenterNode


router = APIRouter()
logger = get_logger("orchestrator")


def get_store() -> MemoryStore:
    """Return the global in-memory store singleton."""
    return store
def get_segmenter() -> SegmenterNode:
    """Default segmenter provider (can be overridden in tests)."""
    return SegmenterNode()

async def get_orchestrator(
    store: MemoryStore = Depends(get_store),
    segmenter: SegmenterNode = Depends(get_segmenter), 
) -> AsyncGenerator[Orchestrator, None]:
    """Yield a per-request Orchestrator instance.

    The Orchestrator delegates flow execution to the LangGraph graph.
    We ensure resources are cleaned up at the end of the request.
    """
    orch = Orchestrator(
        store_=store,
        logger_=logger,
        segmenter=segmenter,    
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
