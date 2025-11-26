"""Endpoints for managing retriever configs and distribution.

Provides simple list/create/update and a test endpoint to exercise a
retriever with a sample query (returns mock results in file-backed mode).
"""

from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter, HTTPException

from .. import storage
from ..schemas import RetrieverConfig, RetrieverUpdate

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
    # Lightweight mock: return a small list of documents and scores
    # Real implementation should call the configured retriever connector.
    q = sample_query.get("query") if isinstance(sample_query, dict) else None
    docs = [
        {"id": "doc1", "score": 0.95, "text": f"Result for {q or 'test'} - 1"},
        {"id": "doc2", "score": 0.78, "text": f"Result for {q or 'test'} - 2"},
    ]
    return {"ok": True, "results": docs}
