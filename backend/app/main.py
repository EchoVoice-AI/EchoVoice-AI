from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .config import get_allowed_origins
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn

from agents.segmenter import segment_user
from agents.retriever import retrieve_citations
from agents.generator import generate_variants
from agents.safety_gate import safety_check_and_filter
from agents.analytics import evaluate_variants
from services.delivery import send_email_mock
from services.logger import get_logger

logger = get_logger('orchestrator')
app = FastAPI(title='EchoVoice-AI Orchestrator')

# CORS middleware (configured via `backend.config`)
origins = get_allowed_origins()

# If running in production with no origins configured, be conservative.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Placeholder router imports (uncomment / implement routers in future)
# from .routers import health, items
# app.include_router(health.router)
# app.include_router(items.router)


class CustomerModel(BaseModel):
    id: Optional[str]
    name: Optional[str]
    email: Optional[str]
    last_event: Optional[str]
    properties: Optional[Dict[str, Any]] = {}


class OrchestrateRequest(BaseModel):
    customer: CustomerModel


@app.post('/orchestrate')
async def orchestrate(payload: OrchestrateRequest):
    customer = payload.customer.dict()
    if not customer:
        raise HTTPException(status_code=400, detail='customer missing')

    # 1. Segmentation
    segment = segment_user(customer)
    logger.info(f"Segment: {segment}")

    # 2. Retrieval
    citations = retrieve_citations(customer)
    logger.info(f"Citations: {citations}")

    # 3. Generation
    variants = generate_variants(customer, segment, citations)
    logger.info(f"Generated {len(variants)} variants")

    # 4. Safety checks
    safety = safety_check_and_filter(variants)
    logger.info(f"Safety safe={len(safety['safe'])} blocked={len(safety['blocked'])}")

    # 5. Analytics / choose winner
    analysis = evaluate_variants(safety['safe'], customer)
    winner = analysis.get('winner')

    # 6. Delivery (mock) — send winner if present
    delivery_result = None
    if winner:
        variant = next((v for v in safety['safe'] if v.get('id') == winner['variant_id']), None)
        if variant:
            delivery_result = send_email_mock(customer.get('email'), variant.get('subject'), variant.get('body'))

    response = {
        'segment': segment,
        'citations': citations,
        'variants': variants,
        'safety': safety,
        'analysis': analysis,
        'delivery': delivery_result
    }
    return response


if __name__ == '__main__':
    # Run with Uvicorn for development
    uvicorn.run(app, host='127.0.0.1', port=8000)
