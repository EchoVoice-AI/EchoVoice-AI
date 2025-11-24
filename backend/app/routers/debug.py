from fastapi import APIRouter, Depends, Query
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.graph.orchestrator import Orchestrator
from app.routers.orchestrator import get_orchestrator
from services.logger import get_logger

logger = get_logger("routers.debug")

router = APIRouter(prefix="/debug", tags=["debug"])


class Preview(BaseModel):
    user_id: str
    email: str
    subject: Optional[str] = None
    body: Optional[str] = None
    variant_id: Optional[str] = None
    blocked: bool = False
    error: Optional[str] = None


class PreviewsResponse(BaseModel):
    previews: List[Preview]


PRECOMPUTED_PREVIEWS = [
    {
        "user_id": "U001",
        "email": "emma@example.com",
        "subject": "Hi Emma, quick note about running shoes",
        "body": "Hi Emma,\n\nWe thought you might like this: …\n\n— Team",
        "variant_id": "A",
        "blocked": False,
    },
    {
        "user_id": "U002",
        "email": "liam@example.com",
        "subject": "Liam, more on the Acme plan",
        "body": "Hello Liam,\n\nDetails: …\nLearn more on our site.",
        "variant_id": "B",
        "blocked": False,
    },
]


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

    if mock:
        return {"previews": PRECOMPUTED_PREVIEWS}

    previews: List[Dict[str, Any]] = []

    for c in mock_customers:
        preview = {
            "user_id": c.get("id"),
            "email": c.get("email"),
            "subject": None,
            "body": None,
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
        else:
            preview["blocked"] = True

        previews.append(preview)

    return {"previews": previews}
