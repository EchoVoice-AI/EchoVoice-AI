"""Retriever service supporting Azure Cognitive Search and selection logic.

This module implements selection (rules/weights/deterministic) and a
connector for Azure Cognitive Search. The connector resolves API keys
from environment variables (by secret ref) and runs either keyword or
vector searches depending on configuration.

The functions are designed to be invoked from the segmentation
retrieval node and from the API test endpoint.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import random
from typing import Any, Dict, List, Optional

from agent.utils.config import get_env

try:
    from azure.core.credentials import AzureKeyCredential  # type: ignore
    from azure.search.documents import SearchClient  # type: ignore
except Exception:
    AzureKeyCredential = None  # type: ignore
    SearchClient = None  # type: ignore


def _match_rule(item: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Evaluate a single rule against provided context.

    Simple equality checking is supported here (op == '==').
    """
    try:
        field = item.get("field")
        op = item.get("op")
        value = item.get("value")
        if field is None:
            return False
        ctx_val = context.get(field)
        if op == "==":
            return ctx_val == value
        if op == "in":
            return ctx_val in value if isinstance(value, (list, tuple, set)) else False
        return False
    except Exception:
        return False


def select_retrievers(
    configs: List[Dict[str, Any]],
    context: Dict[str, Any],
    deterministic_key: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Select retriever configs based on rules, then weights/deterministic hash.

    Returns a list of selected configs (one or more). If any configs match
    rule conditions, those are returned; otherwise we pick a single config by
    weight (deterministic if `deterministic_key` provided, else random).
    """
    enabled = [c for c in configs if c.get("enabled", True)]
    if not enabled:
        return []

    # Rule matching
    matched: List[Dict[str, Any]] = []
    for c in enabled:
        rules = c.get("rules", []) or []
        if not rules:
            continue
        # If any rule matches, include
        for r in rules:
            if _match_rule(r, context):
                matched.append(c)
                break
    if matched:
        return matched

    # No rules matched; pick single config by weight
    total = sum(int(c.get("weight", 0)) for c in enabled)
    if total <= 0:
        # fallback: return first enabled
        return [enabled[0]]

    if deterministic_key:
        h = int(hashlib.sha256(deterministic_key.encode("utf-8")).hexdigest(), 16)
        pick = h % total
    else:
        pick = random.randrange(total)

    cum = 0
    for c in enabled:
        w = int(c.get("weight", 0))
        cum += w
        if pick < cum:
            return [c]

    # Fallback
    return [enabled[-1]]


def _resolve_api_key(secret_ref: str) -> Optional[str]:
    # Check env directly first, then agent utils
    if not secret_ref:
        return None
    val = os.environ.get(secret_ref)
    if val:
        return val
    # fallback to helper
    return get_env(secret_ref)


def _make_search_client(conn: Dict[str, Any]):
    if SearchClient is None or AzureKeyCredential is None:
        return None
    endpoint = conn.get("endpoint")
    index = conn.get("index")
    secret_ref = conn.get("api_key_secret_ref") or conn.get("api_key")
    key = _resolve_api_key(secret_ref) if secret_ref else None
    if not endpoint or not index or not key:
        return None
    try:
        cred = AzureKeyCredential(key)
        client = SearchClient(endpoint=endpoint, index_name=index, credential=cred)
        return client
    except Exception:
        return None


def _format_search_result(hit: Any) -> Dict[str, Any]:
    # `hit` is usually a Mapping-like object returned by the SDK
    try:
        d = dict(hit)
    except Exception:
        d = {"raw": str(hit)}
    # search SDK often includes '@search.score'
    score = d.get("@search.score") or d.get("score")
    text = d.get("content") or d.get("text") or d.get("body") or ""
    return {"id": d.get("id"), "score": score, "text": text, "raw": d}


def _azure_search_sync(conn: Dict[str, Any], query: str, k: int = 5, vector: Optional[List[float]] = None):
    client = _make_search_client(conn)
    if client is None:
        # Return mock data when client isn't available
        return [{"id": "mock1", "score": 1.0, "text": f"Mock result for {query}"}]

    use_vector = bool(conn.get("use_vector"))
    vf = conn.get("vector_field")
    results = []
    try:
        if use_vector and vector is not None and vf:
            # SDK vector search: pass vector param
            hits = client.search(None, vector=vector, top=k)
        else:
            hits = client.search(query, top=k)

        for h in hits:
            results.append(_format_search_result(h))
    except Exception:
        # On failure return empty list (caller can fallback)
        return []
    return results


async def run_single_retriever(conn: Dict[str, Any], query: str, k: int = 5, timeout: float = 6.0, vector: Optional[List[float]] = None) -> List[Dict[str, Any]]:
    """Run a single retriever connector with timeout; uses thread executor for blocking SDK."""
    try:
        return await asyncio.wait_for(asyncio.to_thread(_azure_search_sync, conn, query, k, vector), timeout=timeout)
    except asyncio.TimeoutError:
        return []
    except Exception:
        return []


async def run_retriever_chain(
    configs: List[Dict[str, Any]],
    query: str,
    context: Dict[str, Any],
    k: int = 5,
    timeout: float = 6.0,
    deterministic_key: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Select retrievers and run them, returning deduped aggregated results.

    This function selects retrievers using `select_retrievers` then calls
    `run_single_retriever` for each selected config and aggregates results.
    """
    selected = select_retrievers(configs, context, deterministic_key=deterministic_key)
    if not selected:
        return []

    aggregated: List[Dict[str, Any]] = []
    seen_ids = set()
    for c in selected:
        conn = c.get("connection", {})
        strategy = c.get("strategy", {}) or {}
        kk = int(strategy.get("k", k))
        vec = context.get("query_vector") if context else None
        hits = await run_single_retriever(conn, query, kk, timeout=timeout, vector=vec)
        for h in hits:
            hid = h.get("id")
            if hid and hid in seen_ids:
                continue
            if hid:
                seen_ids.add(hid)
            aggregated.append(h)

    # sort by score descending when available
    try:
        aggregated.sort(key=lambda x: (x.get("score") or 0), reverse=True)
    except Exception:
        pass
    return aggregated
