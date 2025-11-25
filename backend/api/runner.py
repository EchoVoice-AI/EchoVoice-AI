"""Lightweight execution runner for the compiled LangGraph-like pipeline.

This module provides a simple orchestration used by the API to execute a
sequence of phase nodes (segmentation -> priority -> retrieval/generation ->
experimentation -> deployment). It emits WebSocket events via the shared
`ws.manager` so frontend clients can subscribe to `execution.*` events.

The runner intentionally keeps things simple and calls the node callables
declared in `src/agent/phases` and `src/agent/graph.py`. It collects outputs
into a plain dict that matches `agent.state.GraphState` fields used by the
pipeline nodes.
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any, Dict

from src.agent.graph import deployment_node
from src.agent.phases.experimentation.experiment import experimentation_node
from src.agent.phases.generation.generate import generation_node
from src.agent.phases.segmentation.behavioral import behavioral_segmentor_node
from src.agent.phases.segmentation.intent import intent_segmentor_node
from src.agent.phases.segmentation.priority import priority_node, priority_router
from src.agent.phases.segmentation.profile import profile_segmentor_node
from src.agent.phases.segmentation.retrieval import retrieval_node

# Import node callables from the agent package
from src.agent.phases.segmentation.rfm import rfm_segmentor_node

from .ws import manager

# In-memory run store for quick status/log access. Suitable for dev only.
EXEC_RUNS: Dict[str, Dict[str, Any]] = {}


def _init_run(run_id: str, initial_state: Dict[str, Any]) -> None:
    EXEC_RUNS[run_id] = {
        "run_id": run_id,
        "status": "queued",
        "logs": [],
        "result": None,
        "state": initial_state,
    }


async def _invoke_node(node_callable, state: Dict[str, Any], node_name: str) -> Dict[str, Any]:
    """Invoke a node callable handling both async and sync callables.

    Many nodes accept `(state, runtime)`; we call with `(state, None)` where
    possible, otherwise with just `state`.
    """
    async def _call_async():
        try:
            return await node_callable(state, None)
        except TypeError:
            return await node_callable(state)

    def _call_sync():
        try:
            return node_callable(state, None)
        except TypeError:
            return node_callable(state)

    try:
        if asyncio.iscoroutinefunction(node_callable):
            out = await _call_async()
        else:
            out = _call_sync()
    except Exception as exc:  # pragma: no cover - bubble up errors to logs
        out = {"error": str(exc)}
    # Normalize None -> {}
    if out is None:
        out = {}
    return out


async def run_graph(initial_state: Dict[str, Any], run_id: str | None = None) -> Dict[str, Any]:
    """Execute the simple pipeline and broadcast `execution.*` events.

    Returns the final GraphState-like dict when finished.
    """
    run_id = run_id or str(uuid.uuid4())
    _init_run(run_id, initial_state)
    EXEC_RUNS[run_id]["status"] = "running"
    await manager.broadcast({"type": "execution.started", "run_id": run_id, "state": initial_state})

    state = initial_state

    # Phase 1: Parallel segmentation nodes
    seg_nodes = [
        ("rfm_segmentor_node", rfm_segmentor_node),
        ("intent_segmentor_node", intent_segmentor_node),
        ("behavioral_segmentor_node", behavioral_segmentor_node),
        ("profile_segmentor_node", profile_segmentor_node),
    ]

    async def _run_and_broadcast(name, fn):
        await manager.broadcast({"type": "execution.node.started", "run_id": run_id, "node": name})
        out = await _invoke_node(fn, state, name)
        # Attach results under a consistent key if provided
        if isinstance(out, dict):
            state.update(out)
        await manager.broadcast({"type": "execution.node.finished", "run_id": run_id, "node": name, "output": out})
        EXEC_RUNS[run_id]["logs"].append({"node": name, "output": out})

    # Run segmentation nodes concurrently
    await asyncio.gather(*[_run_and_broadcast(n, f) for n, f in seg_nodes])

    # Phase 2: Priority (join)
    await manager.broadcast({"type": "execution.node.started", "run_id": run_id, "node": "priority_node"})
    pr_out = await _invoke_node(priority_node, state, "priority_node")
    if isinstance(pr_out, dict):
        state.update(pr_out)
    await manager.broadcast({"type": "execution.node.finished", "run_id": run_id, "node": "priority_node", "output": pr_out})
    EXEC_RUNS[run_id]["logs"].append({"node": "priority_node", "output": pr_out})

    # Decide route
    try:
        # priority_router expects GraphState-like mapping
        next_node = priority_router(state)
    except Exception:
        next_node = "generation_node"

    # If retrieval path requested
    if next_node == "retrieval_node":
        await manager.broadcast({"type": "execution.node.started", "run_id": run_id, "node": "retrieval_node"})
        ret_out = await _invoke_node(retrieval_node, state, "retrieval_node")
        if isinstance(ret_out, dict):
            state.update(ret_out)
        await manager.broadcast({"type": "execution.node.finished", "run_id": run_id, "node": "retrieval_node", "output": ret_out})
        EXEC_RUNS[run_id]["logs"].append({"node": "retrieval_node", "output": ret_out})

    # Generation
    await manager.broadcast({"type": "execution.node.started", "run_id": run_id, "node": "generation_node"})
    gen_out = await _invoke_node(generation_node, state, "generation_node")
    if isinstance(gen_out, dict):
        state.update(gen_out)
    await manager.broadcast({"type": "execution.node.finished", "run_id": run_id, "node": "generation_node", "output": gen_out})
    EXEC_RUNS[run_id]["logs"].append({"node": "generation_node", "output": gen_out})

    # Experiments
    await manager.broadcast({"type": "execution.node.started", "run_id": run_id, "node": "experimentation_node"})
    exp_out = await _invoke_node(experimentation_node, state, "experimentation_node")
    if isinstance(exp_out, dict):
        state.update(exp_out)
    await manager.broadcast({"type": "execution.node.finished", "run_id": run_id, "node": "experimentation_node", "output": exp_out})
    EXEC_RUNS[run_id]["logs"].append({"node": "experimentation_node", "output": exp_out})

    # Deployment
    await manager.broadcast({"type": "execution.node.started", "run_id": run_id, "node": "deployment_node"})
    dep_out = await _invoke_node(deployment_node, state, "deployment_node")
    if isinstance(dep_out, dict):
        state.update(dep_out)
    await manager.broadcast({"type": "execution.node.finished", "run_id": run_id, "node": "deployment_node", "output": dep_out})
    EXEC_RUNS[run_id]["logs"].append({"node": "deployment_node", "output": dep_out})

    # Finalize
    EXEC_RUNS[run_id]["status"] = "finished"
    EXEC_RUNS[run_id]["result"] = state
    await manager.broadcast({"type": "execution.finished", "run_id": run_id, "final_state": state})
    return state


def get_run_status(run_id: str) -> Dict[str, Any] | None:
    return EXEC_RUNS.get(run_id)


def list_runs() -> Dict[str, Dict[str, Any]]:
    return EXEC_RUNS
