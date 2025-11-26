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
import importlib
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

from . import storage
from .config import SETTINGS
from .ws import manager

# In-memory run store for quick status/log access. Suitable for dev only.
EXEC_RUNS: Dict[str, Dict[str, Any]] = {}
RUN_TASKS: Dict[str, asyncio.Task] = {}


def _init_run(run_id: str, initial_state: Dict[str, Any]) -> None:
    EXEC_RUNS[run_id] = {
        "run_id": run_id,
        "status": "queued",
        "logs": [],
        "result": None,
        "state": initial_state,
    }


def _resolve_callable_from_string(path: str):
    """Resolve a dotted import path to a callable, e.g. 'pkg.module.func'."""
    if not path or not isinstance(path, str):
        return None
    try:
        module_path, attr = path.rsplit(".", 1)
    except Exception:
        return None
    try:
        mod = importlib.import_module(module_path)
        return getattr(mod, attr, None)
    except Exception:
        return None


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
    # If the run has not been initialized (caller may have already), ensure it exists
    if run_id not in EXEC_RUNS:
        _init_run(run_id, initial_state)
    EXEC_RUNS[run_id]["status"] = "running"
    await manager.broadcast({"type": "execution.started", "run_id": run_id, "state": initial_state})
    # persist status if DB enabled
    try:
        if getattr(storage, "USE_DB", False) and getattr(storage, "_db", None) is not None:
            try:
                storage._db.update_run_status(run_id, "running")
            except Exception:
                pass
    except Exception:
        pass

    # Load persisted graph configuration
    cfg = storage.load_graph_config()
    nodes_cfg = {n.get("id"): n for n in cfg.get("nodes", [])}
    edges = cfg.get("edges", [])

    # Build adjacency and predecessor counts (in-degree), excluding START as predecessor
    adj: Dict[str, list] = {}
    preds: Dict[str, set] = {}
    for e in edges:
        frm = e.get("from")
        to = e.get("to")
        if frm is None or to is None:
            continue
        adj.setdefault(frm, []).append(e)
        if frm != "START":
            preds.setdefault(to, set()).add(frm)

    in_deg: Dict[str, int] = {}
    for node_id in nodes_cfg.keys():
        in_deg[node_id] = len(preds.get(node_id, set()))

    # frontier starts with nodes directly reachable from START
    frontier = [e.get("to") for e in edges if e.get("from") == "START"]
    # canonical mapping of known callables
    NODE_CALLABLES = {
        "rfm_segmentor_node": rfm_segmentor_node,
        "intent_segmentor_node": intent_segmentor_node,
        "behavioral_segmentor_node": behavioral_segmentor_node,
        "profile_segmentor_node": profile_segmentor_node,
        "priority_node": priority_node,
        "retrieval_node": retrieval_node,
        "generation_node": generation_node,
        "experimentation_node": experimentation_node,
        "deployment_node": deployment_node,
    }

    # Dynamic discovery: allow nodes to declare a dotted `callable` path
    # in the persisted graph config. If present, resolve and add to mapping.
    for nid, spec in nodes_cfg.items():
        if nid in NODE_CALLABLES:
            continue
        if not isinstance(spec, dict):
            continue
        cpath = spec.get("callable") or spec.get("handler")
        if not cpath:
            continue
        resolved = _resolve_callable_from_string(cpath)
        if resolved is not None:
            NODE_CALLABLES[nid] = resolved

    ROUTERS = {
        "priority_node": priority_router,
    }

    state = initial_state

    processed = set()

    async def _run_and_broadcast(name, fn):
        await manager.broadcast({"type": "execution.node.started", "run_id": run_id, "node": name})
        out = await _invoke_node(fn, state, name)
        if isinstance(out, dict):
            state.update(out)
        await manager.broadcast({"type": "execution.node.finished", "run_id": run_id, "node": name, "output": out})
        EXEC_RUNS[run_id]["logs"].append({"node": name, "output": out})
        # persist log to DB when available
        try:
            if getattr(storage, "USE_DB", False) and getattr(storage, "_db", None) is not None:
                storage._db.append_run_log(run_id, {"node": name, "output": out})
        except Exception:
            pass

    total_nodes = len(nodes_cfg)
    # main execution loop: run ready nodes in parallel, honor joins and conditional routing
    while frontier:
        # remove already processed nodes from frontier
        frontier = [n for n in frontier if n and n not in processed]
        if not frontier:
            break
        # execute all frontier nodes concurrently
        tasks = []
        for node_id in frontier:
            fn = NODE_CALLABLES.get(node_id)
            if fn is None:
                # unknown node: skip but mark as processed
                err = {"node": node_id, "output": {"error": "unknown node callable"}}
                EXEC_RUNS[run_id]["logs"].append(err)
                # persist unknown-node log
                try:
                    if getattr(storage, "USE_DB", False) and getattr(storage, "_db", None) is not None:
                        storage._db.append_run_log(run_id, err)
                except Exception:
                    pass
                processed.add(node_id)
                continue
            tasks.append(_run_and_broadcast(node_id, fn))
        # await tasks
        if tasks:
            await asyncio.gather(*tasks)

        # mark frontier nodes processed
        for node_id in list(frontier):
            processed.add(node_id)
            # determine successors
            for e in adj.get(node_id, []):
                to = e.get("to")
                # conditional router handling
                if node_id in ROUTERS:
                    try:
                        router_out = ROUTERS[node_id](state)
                    except Exception:
                        router_out = None
                    # only follow the edge that matches router_out
                    if router_out != to:
                        continue
                    # when routed, treat as immediate successor (no join semantics)
                    in_deg[to] = max(0, in_deg.get(to, 0) - 1)
                    if in_deg.get(to, 0) == 0:
                        frontier.append(to)
                else:
                    # normal edge: decrement in-degree and enqueue when zero
                    in_deg[to] = max(0, in_deg.get(to, 0) - 1)
                    if in_deg.get(to, 0) == 0:
                        frontier.append(to)

        # prune frontier for next loop
        frontier = [n for n in frontier if n not in processed]

        # safety: detect cycles where nothing progresses
        if len(processed) >= total_nodes:
            break


    try:
        # Finalize
        EXEC_RUNS[run_id]["status"] = "finished"
        EXEC_RUNS[run_id]["result"] = state
        # persist final result and status
        try:
            if getattr(storage, "USE_DB", False) and getattr(storage, "_db", None) is not None:
                storage._db.set_run_result(run_id, state)
                storage._db.update_run_status(run_id, "finished")
        except Exception:
            pass

        await manager.broadcast({"type": "execution.finished", "run_id": run_id, "final_state": state})
        # After finishing, attempt to start queued runs if any
        try:
            if getattr(storage, "USE_DB", False) and getattr(storage, "_db", None) is not None:
                _maybe_start_queued_runs()
        except Exception:
            pass
        return state
    except asyncio.CancelledError:
        # Task was cancelled; mark run cancelled and broadcast
        EXEC_RUNS[run_id]["status"] = "cancelled"
        try:
            if getattr(storage, "USE_DB", False) and getattr(storage, "_db", None) is not None:
                storage._db.update_run_status(run_id, "cancelled")
        except Exception:
            pass
        await manager.broadcast({"type": "execution.cancelled", "run_id": run_id, "state": state})
        # trigger queued runs too
        try:
            if getattr(storage, "USE_DB", False) and getattr(storage, "_db", None) is not None:
                _maybe_start_queued_runs()
        except Exception:
            pass
        raise
    except Exception as exc:  # pragma: no cover - unexpected
        EXEC_RUNS[run_id]["status"] = "failed"
        EXEC_RUNS[run_id]["result"] = {"error": str(exc)}
        try:
            if getattr(storage, "USE_DB", False) and getattr(storage, "_db", None) is not None:
                storage._db.set_run_result(run_id, {"error": str(exc)})
                storage._db.update_run_status(run_id, "failed")
        except Exception:
            pass
        await manager.broadcast({"type": "execution.error", "run_id": run_id, "error": str(exc)})
        try:
            if getattr(storage, "USE_DB", False) and getattr(storage, "_db", None) is not None:
                _maybe_start_queued_runs()
        except Exception:
            pass
        return EXEC_RUNS[run_id]["result"]


def start_async_run(initial_state: Dict[str, Any], run_id: str | None = None) -> str:
    """Create and track an asyncio Task for the run, return the run_id."""
    run_id = run_id or str(uuid.uuid4())
    _init_run(run_id, initial_state)

    # If DB mode enabled, use DB helpers to coordinate concurrency
    try:
        if getattr(storage, "USE_DB", False) and getattr(storage, "_db", None) is not None:
            max_conc = getattr(SETTINGS, "max_concurrent_runs", 4)
            active = storage._db.count_active_runs()
            # persist run as queued or running depending on capacity
            if active >= int(max_conc):
                storage._db.create_run(run_id, initial_state, status="queued")
                EXEC_RUNS[run_id]["status"] = "queued"
                return run_id
            else:
                storage._db.create_run(run_id, initial_state, status="running")
    except Exception:
        # fallback to in-memory if DB helpers fail
        pass

    task = asyncio.create_task(run_graph(initial_state, run_id=run_id))
    RUN_TASKS[run_id] = task

    def _cleanup(t: asyncio.Task):
        # Remove task mapping when done
        RUN_TASKS.pop(run_id, None)

    task.add_done_callback(_cleanup)
    return run_id


def cancel_run(run_id: str) -> bool:
    """Attempt to cancel a running task. Returns True if cancelled or scheduled to cancel."""
    task = RUN_TASKS.get(run_id)
    if task is None:
        # If no running task, but run exists, mark as cancelled if not finished
        meta = EXEC_RUNS.get(run_id)
        if meta and meta.get("status") not in ("finished", "failed", "cancelled"):
            EXEC_RUNS[run_id]["status"] = "cancelled"
            try:
                if getattr(storage, "USE_DB", False) and getattr(storage, "_db", None) is not None:
                    storage._db.update_run_status(run_id, "cancelled")
            except Exception:
                pass
            # attempt to start queued runs now that capacity freed
            try:
                if getattr(storage, "USE_DB", False) and getattr(storage, "_db", None) is not None:
                    _maybe_start_queued_runs()
            except Exception:
                pass
            return True
        return False
    if task.done():
        return False
    # request cancellation
    task.cancel()
    EXEC_RUNS[run_id]["status"] = "cancelling"
    try:
        if getattr(storage, "USE_DB", False) and getattr(storage, "_db", None) is not None:
            storage._db.update_run_status(run_id, "cancelling")
    except Exception:
        pass
    return True


def _maybe_start_queued_runs() -> None:
    """Start queued runs from DB if capacity available.

    This is a simple dispatcher: when runs finish/cancel/failed we look for
    queued runs and start them up to `SETTINGS.max_concurrent_runs`.
    """
    if not getattr(storage, "USE_DB", False) or getattr(storage, "_db", None) is None:
        return
    try:
        max_conc = getattr(SETTINGS, "max_concurrent_runs", 4)
        active = storage._db.count_active_runs()
        capacity = int(max_conc) - int(active)
        if capacity <= 0:
            return
        queued = storage._db.get_queued_runs(limit=capacity)
        for q in queued:
            rid = q.get("id")
            payload = q.get("payload", {})
            # mark as running and start
            try:
                storage._db.update_run_status(rid, "running")
            except Exception:
                pass
            # schedule task
            if rid not in RUN_TASKS and EXEC_RUNS.get(rid) is None:
                _init_run(rid, payload)
                t = asyncio.create_task(run_graph(payload, run_id=rid))
                RUN_TASKS[rid] = t
                def _cleanup2(tk: asyncio.Task, runid=rid):
                    RUN_TASKS.pop(runid, None)
                t.add_done_callback(_cleanup2)
    except Exception:
        pass


def get_run_status(run_id: str) -> Dict[str, Any] | None:
    """Return stored metadata for a run, or None if not found.

    The returned dict contains `status`, `logs`, `result`, and `state` keys.
    """
    return EXEC_RUNS.get(run_id)


def list_runs() -> Dict[str, Dict[str, Any]]:
    """Return the in-memory map of all runs (dev-only)."""
    return EXEC_RUNS
