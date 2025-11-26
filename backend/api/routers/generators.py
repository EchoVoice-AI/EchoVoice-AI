"""Endpoints for managing generator variants and distribution.

Follows the lightweight pattern used by `segments.py`: read via
`storage.load_generators()` and persist via `storage.save_generators()`.
"""

from __future__ import annotations

import asyncio
import json
from typing import List

from fastapi import APIRouter, HTTPException

from .. import storage
from ..schemas import GeneratorUpdate, GeneratorVariant, PreviewRequest, PreviewResponse

# Import the real generator service from the agent phases
try:
    from agent.phases.generation.variants import generate_variants  # type: ignore
except Exception:
    generate_variants = None  # type: ignore

router = APIRouter()


@router.get("/api/generators", response_model=List[GeneratorVariant])
async def list_generators() -> List[GeneratorVariant]:
    """List all generator variants."""
    gens = storage.load_generators()
    return [GeneratorVariant(**g) for g in gens]


@router.post("/api/generators", response_model=GeneratorVariant)
async def create_generator(payload: GeneratorVariant) -> GeneratorVariant:
    """Create a new generator variant."""
    gens = storage.load_generators() or []
    # simple de-dup check
    for g in gens:
        if g.get("id") == payload.id:
            raise HTTPException(status_code=400, detail="Generator id already exists")
    gens.append(payload.dict())
    storage.save_generators(gens)
    return payload


@router.put("/api/generators/{gen_id}", response_model=GeneratorVariant)
async def update_generator(gen_id: str, payload: GeneratorUpdate) -> GeneratorVariant:
    """Update an existing generator variant."""
    gens = storage.load_generators() or []
    found = None
    for g in gens:
        if g.get("id") == gen_id:
            found = g
            break
    if not found:
        raise HTTPException(status_code=404, detail="Generator not found")
    # apply fields
    if payload.name is not None:
        found["name"] = payload.name
    if payload.enabled is not None:
        found["enabled"] = payload.enabled
    if payload.model is not None:
        found["model"] = payload.model
    if payload.prompt_template is not None:
        found["prompt_template"] = payload.prompt_template
    if payload.params is not None:
        found["params"] = payload.params
    if payload.weight is not None:
        found["weight"] = int(payload.weight)
    if payload.rules is not None:
        found["rules"] = payload.rules

    storage.save_generators(gens)
    return GeneratorVariant(**found)


@router.post("/api/generators/preview", response_model=PreviewResponse)
async def preview_generation(payload: PreviewRequest) -> PreviewResponse:
    """Generate a lightweight preview for a given prompt and variant."""
    # Build a safe sample input for the generator service
    sample_input = payload.sample_input or {}
    customer = sample_input.get("customer") or {"id": "sample_user", "name": "Test"}
    segment = sample_input.get("segment") or {"final_segment_label": "test_segment"}
    citations = sample_input.get("citations") or []

    # If the real generator is not available, return a helpful error for the UI
    if generate_variants is None:
        sample = "[preview-mock] generator service unavailable"
        return PreviewResponse(ok=False, output=sample, debug={"error": "generator service not importable"})

    # Call the synchronous generator in a thread to avoid blocking the event loop.
    # Enforce a short timeout to keep the preview snappy in the UI.
    try:
        variants = await asyncio.wait_for(
            asyncio.to_thread(generate_variants, customer, segment, citations),
            timeout=12.0,
        )
        # Return the full variants as JSON string in `output` and some debug info
        out = json.dumps(variants, ensure_ascii=False)
        return PreviewResponse(ok=True, output=out, debug={"count": len(variants)})
    except asyncio.TimeoutError:
        return PreviewResponse(ok=False, output=None, debug={"error": "generator preview timed out"})
    except Exception as exc:
        return PreviewResponse(ok=False, output=None, debug={"error": str(exc)})
