from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Any, Dict, List, Optional
import os
import time

from pydantic import BaseModel

from ..graph.orchestrator import Orchestrator
from .orchestrator import get_orchestrator, OrchestrateRequest
from backend.services.logger import get_logger

logger = get_logger("routers.debug")

router = APIRouter(prefix="/debug", tags=["debug"])


class Preview(BaseModel):
    user_id: str
    email: str
    subject: Optional[str] = None
    body: Optional[str] = None
    # compatibility alias some frontends expect
    body_text: Optional[str] = None
    variant_id: Optional[str] = None
    blocked: bool = False
    error: Optional[str] = None


class PreviewsResponse(BaseModel):
    previews: List[Preview]


# Precomputed mock previews used when ?mock=true
PRECOMPUTED_PREVIEWS = [
    {
        "user_id": "U001",
        "email": "emma@example.com",
        "subject": "Hi Emma, quick note about running shoes",
        "body": "Hi Emma,\n\nWe thought you might like this: …\n\n— Team",
        "body_text": "Hi Emma,\n\nWe thought you might like this: …\n\n— Team",
        "variant_id": "A",
        "blocked": False,
    },
    {
        "user_id": "U002",
        "email": "liam@example.com",
        "subject": "Liam, more on the Acme plan",
        "body": "Hello Liam,\n\nDetails: …\nLearn more on our site.",
        "body_text": "Hello Liam,\n\nDetails: …\nLearn more on our site.",
        "variant_id": "B",
        "blocked": False,
    },
]


# Simple process-local TTL cache for debug previews (dev-only). Keyed by mock flag.
# Each entry: { 'value': <response dict>, 'expires_at': <timestamp> }
_DEBUG_PREVIEWS_CACHE: Dict[str, Dict[str, Any]] = {}


def _get_cache_ttl_seconds() -> Optional[int]:
    v = os.environ.get("ECHO_DEBUG_CACHE_TTL")
    if not v:
        return None
    try:
        t = int(v)
        if t <= 0:
            return None
        return t
    except Exception:
        return None


@router.get("/deliveries", response_model=PreviewsResponse)
async def get_debug_deliveries(
    orchestrator: Orchestrator = Depends(get_orchestrator),
    mock: bool = Query(False, description="Return precomputed mock previews without running pipeline"),
) -> Dict[str, Any]:
    """
    Debug endpoint (Issue #11).

    Runs the lightweight orchestrator for a couple of mock customers and
    returns only the email preview outputs (to, subject, body) suitable
    for the UI preview.
    """

    mock_customers = [
        {"id": "U001", "name": "Emma", "email": "emma@example.com"},
        {"id": "U002", "name": "Liam", "email": "liam@example.com"},
    ]

    cache_ttl = _get_cache_ttl_seconds()
    cache_key = f"mock={bool(mock)}"

    # Serve cached response when TTL enabled and cache valid
    if cache_ttl:
        entry = _DEBUG_PREVIEWS_CACHE.get(cache_key)
        if entry and entry.get("expires_at", 0) > time.time():
            logger.debug("returning cached debug previews for %s", cache_key)
            return entry["value"]

    if mock:
        response = {"previews": PRECOMPUTED_PREVIEWS}
        if cache_ttl:
            _DEBUG_PREVIEWS_CACHE[cache_key] = {"value": response, "expires_at": time.time() + cache_ttl}
        return response

    previews: List[Dict[str, Any]] = []

    for c in mock_customers:
        preview = {
            "user_id": c.get("id"),
            "email": c.get("email"),
            "subject": None,
            "body": None,
            "body_text": None,
            "variant_id": None,
            "blocked": False,
            "error": None,
        }

        try:
            result = await orchestrator.run_flow("default_personalization", c)
        except Exception:
            logger.exception("debug preview run_flow failed for %s", c.get("id"))
            preview["error"] = "pipeline failed"
            previews.append(preview)
            continue

        # Extract winner (if any) and safe variants
        winner = result.get("analysis", {}).get("winner") if isinstance(result.get("analysis"), dict) else None
        safe_variants = result.get("safety", {}).get("safe", []) if isinstance(result.get("safety"), dict) else []

        variant = None
        if winner and isinstance(winner, dict):
            variant_id = winner.get("variant_id")
            variant = next((v for v in safe_variants if v.get("id") == variant_id), None)

        # Fallback: use first safe variant if no explicit winner
        if not variant and safe_variants:
            variant = safe_variants[0]

        if variant:
            preview["variant_id"] = variant.get("id")
            preview["subject"] = variant.get("subject")
            preview["body"] = variant.get("body")
            # compatibility alias for frontends that look for `body_text`
            preview["body_text"] = variant.get("body")
        else:
            preview["blocked"] = True

        previews.append(preview)

    response = {"previews": previews}
    if cache_ttl:
        _DEBUG_PREVIEWS_CACHE[cache_key] = {"value": response, "expires_at": time.time() + cache_ttl}
    return response


@router.post("/run")
async def debug_run_pipeline(
    payload: OrchestrateRequest,
    orchestrator: Orchestrator = Depends(get_orchestrator),
) -> Dict[str, Any]:
    """
    Debug endpoint (Issue #10).

    Runs the full orchestrator pipeline for a single customer and returns
    the complete MessageState (all intermediate results) for debugging.
    
    This endpoint returns the full orchestrator result including:
    - segment
    - citations
    - variants
    - safety
    - analysis
    - delivery
    """
    customer = payload.customer.model_dump()
    if not customer:
        raise HTTPException(status_code=400, detail="customer missing")
    
    logger.info("debug/run for customer %s", customer.get("id") or customer.get("email"))
    result = await orchestrator.run_flow("default_personalization", customer)
    return result
