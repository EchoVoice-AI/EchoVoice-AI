"""Endpoints for managing retriever configs and distribution.

Provides simple list/create/update and a test endpoint to exercise a
retriever with a sample query (returns mock results in file-backed mode).
"""

from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter, HTTPException

from .. import storage
from ..schemas import RetrieverConfig, RetrieverUpdate
import asyncio
from typing import Any

# Try to import the retriever runtime service (optional)
try:
    from agent.services.retriever import run_retriever_chain  # type: ignore
except Exception:
    run_retriever_chain = None  # type: ignore

router = APIRouter()


@router.get("/api/retrievers", response_model=List[RetrieverConfig])
async def list_retrievers() -> List[RetrieverConfig]:
    """List all retriever configurations."""
    items = storage.load_retrievers() or []
    return [RetrieverConfig(**r) for r in items]


@router.post("/api/retrievers", response_model=RetrieverConfig)
async def create_retriever(payload: RetrieverConfig) -> RetrieverConfig:
    """Create a new retriever configuration."""
    items = storage.load_retrievers() or []
    for r in items:
        if r.get("id") == payload.id:
            raise HTTPException(status_code=400, detail="Retriever id already exists")
    items.append(payload.dict())
    storage.save_retrievers(items)
    return payload


@router.put("/api/retrievers/{ret_id}", response_model=RetrieverConfig)
async def update_retriever(ret_id: str, payload: RetrieverUpdate) -> RetrieverConfig:
    """Update an existing retriever configuration."""
    items = storage.load_retrievers() or []
    found = None
    for r in items:
        if r.get("id") == ret_id:
            found = r
            break
    if not found:
        raise HTTPException(status_code=404, detail="Retriever not found")
    if payload.name is not None:
        found["name"] = payload.name
    if payload.enabled is not None:
        found["enabled"] = payload.enabled
    if payload.connection is not None:
        found["connection"] = payload.connection
    if payload.strategy is not None:
        found["strategy"] = payload.strategy
    if payload.weight is not None:
        found["weight"] = int(payload.weight)

    storage.save_retrievers(items)
    return RetrieverConfig(**found)


@router.post("/api/retrievers/test")
async def test_retriever(sample_query: Dict) -> Dict:
    """Test the retriever with a sample query."""
    q = sample_query.get("query") if isinstance(sample_query, dict) else None
    retriever_id = sample_query.get("retriever_id") if isinstance(sample_query, dict) else None

    # If a retriever_id is supplied and the runtime service is available,
    # call the same code path the node uses for realistic results.
    if retriever_id and run_retriever_chain is not None:
        items = storage.load_retrievers() or []
        cfg = None
        for it in items:
            if it.get("id") == retriever_id:
                cfg = it
                break
        if cfg is None:
            raise HTTPException(status_code=404, detail="Retriever not found")

        # run the retriever chain with only this config
        try:
            results = await asyncio.wait_for(
                run_retriever_chain([cfg], q or "", {}, k=5, timeout=6.0),
                timeout=8.0,
            )
            return {"ok": True, "results": results}
        except asyncio.TimeoutError:
            return {"ok": False, "error": "retriever test timed out"}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    # Fallback mock
    docs: List[Dict[str, Any]] = [
        {"id": "doc1", "score": 0.95, "text": f"Result for {q or 'test'} - 1"},
        {"id": "doc2", "score": 0.78, "text": f"Result for {q or 'test'} - 2"},
    ]
    return {"ok": True, "results": docs}
