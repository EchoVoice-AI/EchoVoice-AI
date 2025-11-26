from __future__ import annotations

import uuid
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from .. import runner, storage
from ..schemas import GraphSummary, ValidationResult
from ..ws import manager

router = APIRouter()


@router.get("/api/graph", response_model=GraphSummary)
async def get_graph() -> GraphSummary:
    try:
        nodes = storage.default_segments_from_graph()
        node_names = [s["name"] for s in nodes]
    except Exception:
        node_names = []
    return GraphSummary(name="EchoVoice Agent Graph", nodes=node_names)


@router.get("/api/graph/config")
async def get_graph_config() -> Dict[str, Any]:
    cfg = storage.load_graph_config()
    return cfg


@router.put("/api/graph/config")
async def put_graph_config(payload: Dict[str, Any]):
    if not isinstance(payload, dict) or "nodes" not in payload or "edges" not in payload:
        raise HTTPException(status_code=400, detail="Invalid graph config payload")
    try:
        storage.save_graph_config(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    await manager.broadcast({"type": "graph.config.updated", "config": payload})
    return JSONResponse({"saved": True})


@router.post("/api/graph/execute")
async def execute_graph(request: Dict[str, Any]):
    run_req = request.get("run_request") if isinstance(request, dict) else None
    if run_req is None:
        raise HTTPException(status_code=400, detail="Missing 'run_request' payload")
    async_mode = bool(request.get("async", True)) if isinstance(request, dict) else True

    if async_mode:
        run_id = runner.start_async_run(run_req)
        return JSONResponse({"run_id": run_id, "status": "queued"})
    else:
        run_id = str(uuid.uuid4())
        result = await runner.run_graph(run_req, run_id=run_id)
        return JSONResponse({"run_id": run_id, "status": "finished", "result": result})


@router.delete("/api/graph/execute/{run_id}/cancel")
async def cancel_execute(run_id: str):
    ok = runner.cancel_run(run_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Run not found or already finished")
    await manager.broadcast({"type": "execution.cancel.requested", "run_id": run_id})
    return JSONResponse({"cancel_requested": True})


@router.get("/api/graph/execute/{run_id}/status")
async def get_execute_status(run_id: str):
    s = runner.get_run_status(run_id)
    if s is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return s


@router.get("/api/graph/execute/{run_id}/logs")
async def get_execute_logs(run_id: str):
    s = runner.get_run_status(run_id)
    if s is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return {"logs": s.get("logs", [])}


@router.post("/api/graph/validate", response_model=ValidationResult)
async def validate_graph() -> ValidationResult:
    segments = storage.load_segments()
    errors: List[str] = []
    if not any(s.get("enabled") for s in segments):
        errors.append("At least one segment must be enabled.")
    for s in segments:
        p = s.get("priority")
        try:
            pv = float(p)
            if not (0.0 <= pv <= 1e6):
                errors.append(f"Segment {s.get('id')} has invalid priority: {p}")
        except Exception:
            errors.append(f"Segment {s.get('id')} has non-numeric priority: {p}")
    valid = len(errors) == 0
    return ValidationResult(valid=valid, errors=errors)


@router.post("/api/graph/validate-config", response_model=ValidationResult)
async def validate_graph_config() -> ValidationResult:
    cfg = storage.load_graph_config()
    nodes = cfg.get("nodes", [])
    edges = cfg.get("edges", [])
    errors: List[str] = []

    builtin = {
        "rfm_segmentor_node",
        "intent_segmentor_node",
        "behavioral_segmentor_node",
        "profile_segmentor_node",
        "priority_node",
        "retrieval_node",
        "generation_node",
        "experimentation_node",
        "deployment_node",
    }

    node_map = {n.get("id"): n for n in nodes}

    import importlib

    for nid, spec in node_map.items():
        if not isinstance(spec, dict):
            errors.append(f"Node {nid} has invalid spec")
            continue
        cpath = spec.get("callable") or spec.get("handler")
        if cpath:
            try:
                module_path, attr = cpath.rsplit(".", 1)
                mod = importlib.import_module(module_path)
                if not hasattr(mod, attr):
                    errors.append(f"Callable {cpath} for node {nid} not found")
            except Exception:
                errors.append(f"Callable {cpath} for node {nid} could not be imported")
        else:
            if nid not in builtin:
                errors.append(f"Unknown node id '{nid}' with no callable specified")

    adj: Dict[str, list] = {}
    in_deg: Dict[str, int] = {nid: 0 for nid in node_map.keys()}
    for e in edges:
        frm = e.get("from")
        to = e.get("to")
        if frm is None or to is None:
            continue
        if frm == "START":
            adj.setdefault(frm, []).append(to)
            in_deg[to] = in_deg.get(to, 0)
            continue
        adj.setdefault(frm, []).append(to)
        in_deg[to] = in_deg.get(to, 0) + 1

    q = [n for n, d in in_deg.items() if d == 0]
    processed = 0
    while q:
        n = q.pop(0)
        processed += 1
        for nb in adj.get(n, []):
            in_deg[nb] = in_deg.get(nb, 1) - 1
            if in_deg[nb] == 0:
                q.append(nb)

    if processed < len(node_map):
        errors.append("Graph contains a cycle or disconnected nodes preventing topological order")

    valid = len(errors) == 0
    return ValidationResult(valid=valid, errors=errors)


@router.post("/api/graph/commit")
async def commit_graph(message: str | None = None):
    segments = storage.load_segments()
    path = storage.snapshot_segments(segments, message=message)
    await manager.broadcast({"type": "graph.committed", "path": str(path)})
    return JSONResponse({"committed": True, "path": str(path)})
