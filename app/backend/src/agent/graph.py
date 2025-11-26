"""LangGraph single-node graph template.

Returns a predefined response. Replace logic and configuration as needed.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

from langgraph.graph import START, StateGraph
from langgraph.runtime import Runtime

from agent.phases.experimentation.experiment import experimentation_node
from agent.phases.generation.generate import generation_node
from agent.phases.segmentation.behavioral import behavioral_segmentor_node
from agent.phases.segmentation.intent import intent_segmentor_node
from agent.phases.segmentation.priority import priority_node, priority_router
from agent.phases.segmentation.profile import profile_segmentor_node
from agent.phases.segmentation.retrieval import retrieval_node
from agent.phases.segmentation.rfm import rfm_segmentor_node
from agent.state import Context, GraphState
import asyncio

# Ensure the package root (src/) is on sys.path so absolute imports work
src_root = Path(__file__).resolve().parents[1]
if str(src_root) not in sys.path:
    sys.path.insert(0, str(src_root))


async def deployment_node(
    state: GraphState, runtime: Runtime[Context]
) -> Dict[str, Any]:
    """Deploy selected variant or record deployment metadata (placeholder)."""
    from agent.phases.deployment import deployer

    variant = (
        (state.get("experiment_assignment") or {}).get("variant")
        if isinstance(state, dict)
        else "default"
    )
    status = deployer.deploy(version=str(variant), target="staging")
    return {"deployment_status": status}


# Compose the graph with nodes and edges
graph = (
    StateGraph(GraphState, context_schema=Context)
    # Add segmentation nodes
    .add_node("profile_segmentor_node", profile_segmentor_node)
    .add_node("rfm_segmentor_node", rfm_segmentor_node)
    .add_node("intent_segmentor_node", intent_segmentor_node)
    .add_node("behavioral_segmentor_node", behavioral_segmentor_node)
    .add_node("priority_node", priority_node)
    # Priority → Generation → Experiments → Deployment
    .add_node("retrieval_node", retrieval_node)
    .add_node("generation_node", generation_node)
    .add_node("experimentation_node", experimentation_node)
    .add_node("deployment_node", deployment_node)
    # --- Phase 1: PARALLEL START → ALL SEGMENTATION NODES ---
    .add_edge(START, "rfm_segmentor_node")
    .add_edge(START, "intent_segmentor_node")
    .add_edge(START, "behavioral_segmentor_node")
    .add_edge(START, "profile_segmentor_node")
    # --- Phase 2: ALL SEGMENTORS → PRIORITY (JOIN POINT) ---
    # The default merge is safe as all segmentors write to unique keys.
    .add_edge("rfm_segmentor_node", "priority_node")
    .add_edge("intent_segmentor_node", "priority_node")
    .add_edge("behavioral_segmentor_node", "priority_node")
    .add_edge("profile_segmentor_node", "priority_node")
    # --- Phase 3: CONDITIONAL ROUTING (NEW) ---
    # Decide between Retrieval (RAG) or direct Generation
    .add_conditional_edges(
        "priority_node",
        priority_router,  # The function that returns the next node name
        {
            "retrieval_node": "retrieval_node",  # If critical, go to RAG
            "generation_node": "generation_node",  # If standard, skip RAG
        },
    )
    # --- Phase 4: MERGE RETRIEVAL BACK TO GENERATION ---
    # The RAG flow MUST proceed to generation afterward
    .add_edge("retrieval_node", "generation_node")
    # --- Phase 5: SEQUENTIAL DOWNSTREAM ---
    .add_edge("generation_node", "experimentation_node")
    .add_edge("experimentation_node", "deployment_node")
    # --- Set the END point ---
    .set_finish_point("deployment_node")  # <-- The graph terminates here
    .compile(name="EchoVoice Agent Graph")
)


async def start_node(state: GraphState, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Start node behavior: run all segmentation nodes in parallel and merge outputs.

    This function simulates the START node by invoking the four segmentation
    node callables concurrently and returning their combined outputs.
    """
    # Run segmentation nodes concurrently to mirror the StateGraph START behavior
    tasks = [
        rfm_segmentor_node(state, runtime),
        intent_segmentor_node(state, runtime),
        behavioral_segmentor_node(state, runtime),
        profile_segmentor_node(state, runtime),
    ]
    results = await asyncio.gather(*tasks)
    merged: Dict[str, Any] = {}
    for r in results:
        if isinstance(r, dict):
            merged.update(r)
    return merged


async def run_segmentation_node(state: GraphState, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Compatibility helper that returns segmentation outputs.

    Historically some tests call `run_segmentation_node` after routing. For
    compatibility we simply return any segmentation outputs already present
    on the state (no-op) so downstream nodes can proceed.
    """
    # If segmentation outputs are already present, return them; otherwise no-op
    out = {}
    keys = [
        "rfm_segment_output",
        "intent_segment_output",
        "behavioral_segment_output",
        "profile_segment_output",
    ]
    for k in keys:
        if k in state:
            out[k] = state[k]
    return out
