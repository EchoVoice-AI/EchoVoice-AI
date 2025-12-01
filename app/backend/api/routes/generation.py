"""Phase 3 orchestration routes: Generation & Compliance flow."""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from ..dependencies import get_auth_claims

from PersonalizeAI.nodes.phase3_generation.ai_message_generator import ai_message_generator
from PersonalizeAI.nodes.phase3_generation.compliance_agent import compliance_agent
from PersonalizeAI.nodes.phase3_generation.rewrite_decision import rewrite_decision
from PersonalizeAI.nodes.phase3_generation.automated_rewrite import automated_rewrite

router = APIRouter()


@router.post("/generation/run", tags=["Generation"])
async def run_generation(request: Request, auth_claims: dict = Depends(get_auth_claims)):
    cfg = getattr(request.app.state, "config", None)
    if cfg is None:
        raise HTTPException(status_code=503, detail="App not initialized")

    try:
        payload = await request.json()
    except Exception:
        payload = {}

    state = payload.get("state", {}) or {}

    # Discover clients and helpers from app state / config
    openai_client = cfg.get("openai_client") or cfg.get("openai") or None
    prompt_manager = getattr(request.app.state, "prompty_manager", None)
    approach = cfg.get("approach") or cfg.get("ask_approach") or None

    # Step 1: Generate message variants
    gen_update = await ai_message_generator(state, openai_client=openai_client, prompt_manager=prompt_manager, approach=approach)
    state.update(gen_update)

    # Step 2: Compliance loop
    max_iterations = 3
    iteration = 0
    while True:
        iteration += 1
        comp_update = await compliance_agent(state, openai_client=openai_client, prompt_manager=prompt_manager, approach=approach)
        state.update(comp_update)

        route = rewrite_decision(state)
        if route == "END_PHASE_3":
            break

        if iteration >= max_iterations:
            # Give up after several iterations and return current state
            break

        # Perform automated rewrite for non-compliant variants and loop
        rewrite_update = await automated_rewrite(state, openai_client=openai_client, prompt_manager=prompt_manager, approach=approach)
        state.update(rewrite_update)

    return JSONResponse({"message_variants": state.get("message_variants"), "compliance_log": state.get("compliance_log", [])})
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class GenerationRequest(BaseModel):
    segment_id: str
    goal: str

@router.post("/create-campaign")
async def create_campaign(request: GenerationRequest):
    # Trigger the full workflow: Retrieval -> Generation -> Safety
    # Return generated message variants with citations
    return {"variants": [], "safety_logs": []}