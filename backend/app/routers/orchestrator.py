from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from ..nodes.segmenter_node import SegmenterNode
from ..nodes.retriever_node import RetrieverNode
from ..nodes.generator_node import GeneratorNode
from ..nodes.safety_node import SafetyNode
from ..nodes.analytics_node import AnalyticsNode
from services.delivery import send_email_mock
from services.logger import get_logger
from app.store import MemoryStore, store

router = APIRouter()
logger = get_logger("orchestrator")


def get_store() -> MemoryStore:
    """FastAPI dependency returning the global memory store singleton."""
    return store


class CustomerModel(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    last_event: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)


class OrchestrateRequest(BaseModel):
    customer: CustomerModel


# Instantiate nodes (simple singletons for this router)
segmenter = SegmenterNode()
retriever = RetrieverNode()
generator = GeneratorNode()
safety = SafetyNode()
analytics = AnalyticsNode()


@router.post("/orchestrate")
async def orchestrate(payload: OrchestrateRequest, store: MemoryStore = Depends(get_store)):
    # Use Pydantic v2 model_dump for compatibility with newer versions
    customer = payload.customer.model_dump()
    if not customer:
        raise HTTPException(status_code=400, detail="customer missing")

    # derive a small key for transient state (prefer id, fallback to email)
    key_base = customer.get("id") or customer.get("email") or "anon"

    # 1. Segmentation
    segment = segmenter.run(customer)
    logger.info(f"Segment: {segment}")
    store.set(f"{key_base}:segment", segment)

    # 2. Retrieval
    citations = retriever.run(customer)
    logger.info(f"Citations: {citations}")
    store.set(f"{key_base}:citations", citations)

    # 3. Generation
    variants = generator.run({"customer": customer, "segment": segment, "citations": citations})
    logger.info(f"Generated {len(variants) if variants else 0} variants")
    store.set(f"{key_base}:variants", variants)

    # 4. Safety checks
    safety_result = safety.run(variants)
    safe_count = len(safety_result.get("safe", [])) if isinstance(safety_result, dict) else 0
    blocked_count = len(safety_result.get("blocked", [])) if isinstance(safety_result, dict) else 0
    logger.info(f"Safety safe={safe_count} blocked={blocked_count}")

    # 5. Analytics / choose winner
    analysis = analytics.run({"variants": safety_result.get("safe", []), "customer": customer}) if isinstance(safety_result, dict) else None
    winner = analysis.get("winner") if isinstance(analysis, dict) and analysis else None
    store.set(f"{key_base}:analysis", analysis)
    if winner:
        store.set(f"{key_base}:winner", winner)

    # 6. Delivery (mock)
    delivery_result = None
    if winner and isinstance(safety_result, dict):
        variant = next((v for v in safety_result.get("safe", []) if v.get("id") == winner.get("variant_id")), None)
        if variant:
            delivery_result = send_email_mock(customer.get("email"), variant.get("subject"), variant.get("body"))

    response = {
        "segment": segment,
        "citations": citations,
        "variants": variants,
        "safety": safety_result,
        "analysis": analysis,
        "delivery": delivery_result,
    }
    return response
