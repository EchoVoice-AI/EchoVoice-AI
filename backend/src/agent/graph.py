"""LangGraph single-node graph template.

Returns a predefined response. Replace logic and configuration as needed.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

from langgraph.graph import StateGraph
from langgraph.runtime import Runtime
from typing_extensions import TypedDict

from agent.state import GraphState

# Ensure the package root (src/) is on sys.path so absolute imports work
src_root = Path(__file__).resolve().parents[1]
if str(src_root) not in sys.path:
    sys.path.insert(0, str(src_root))




class Context(TypedDict):
    """Context parameters for the agent.

    Set these when creating assistants OR when invoking the graph.
    See: https://langchain-ai.github.io/langgraph/cloud/how-tos/configuration_cloud/
    """

    my_configurable_param: str


# Use the shared GraphState TypedDict as the state representation for nodes.
State = GraphState


async def start_node(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Start node: normalizes incoming input into state."""
    input_text = (state.get("user_message") or "").strip() if isinstance(state, dict) else ""
    return {"context_query": None, "user_message": input_text}


async def goal_router_node(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Decide which segmentation modules to run."""
    from agent.phases.segmentation import router as segmentation_router

    text = state.get("user_message") if isinstance(state, dict) else ""
    # router exposes `goal_router` which returns a node key
    selected = segmentation_router.goal_router(state if isinstance(state, dict) else {"user_message": text})
    return {"raw_segments": {selected: {"note": "routed"}}, "_selected_segment": selected}


async def run_segmentation_node(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Run the segmentation modules and collect raw outputs."""
    from agent.phases.segmentation import behavioral, intent, profile, rfm

    # Pass the full shared state dict to each segmenter (they accept GraphState)
    shared_state = state if isinstance(state, dict) else {}

    raw_outputs = {}

    # Call concrete segmenter functions
    try:
        r = rfm.rfm_segmenter(shared_state)
    except Exception:
        r = rfm.segment_rfm({"text": shared_state.get("user_message")})
    try:
        it = intent.intent_segmenter(shared_state)
    except Exception:
        it = intent.segment_intent({"text": shared_state.get("user_message")})
    try:
        b = behavioral.behavioral_segmenter(shared_state)
    except Exception:
        b = behavioral.segment_behavioral({"text": shared_state.get("user_message")})
    try:
        p = profile.profile_segmenter(shared_state)
    except Exception:
        p = profile.segment_profile({"text": shared_state.get("user_message")})

    raw_outputs["rfm"] = r
    raw_outputs["intent"] = it
    raw_outputs["behavioral"] = b
    raw_outputs["profile"] = p

    # Normalize outputs into a list of simple segment dicts for prioritization
    def normalize(name: str, module_out: Dict[str, Any]) -> Dict[str, Any]:
        # module_out expected like {"raw_segmentation_data": {name: {"label":..., "confidence":..., "justification":...}}}
        data = module_out.get("raw_segmentation_data", {}) if isinstance(module_out, dict) else {}
        entry = data.get(name, {})
        label = entry.get("label") or entry.get("segment") or name
        score = entry.get("confidence") or entry.get("score") or 0.0
        details = {k: v for k, v in entry.items() if k not in ("label", "confidence", "score")}
        return {"segment": f"{name}:{label}", "score": float(score), "details": details}

    # If the router selected a preferred module, boost its score so routing
    # drives the final prioritized segment (router acts as a gate/priority hint).
    selected = shared_state.get("_selected_segment")
    # Map router node ids to short segment keys used by segmenters
    if isinstance(selected, str):
        sel = selected.lower()
        if "rfm" in sel:
            selected_key = "rfm"
        elif "intent" in sel:
            selected_key = "intent"
        elif "behavioral" in sel:
            selected_key = "behavioral"
        elif "profile" in sel:
            selected_key = "profile"
        else:
            selected_key = None
    else:
        selected_key = None

    segments_list = []
    for name in ("rfm", "intent", "behavioral", "profile"):
        seg = normalize(name, raw_outputs[name])
        if selected_key and selected_key == name:
            # boost selected segment to ensure router preference wins
            seg["score"] = min(1.0, seg.get("score", 0.0) + 1.0)
        segments_list.append(seg)

    return {"raw_segments": raw_outputs, "_segments_for_priority": segments_list}


async def priority_node(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Merge segmentation outputs and choose the final prioritized segment."""
    from agent.phases.segmentation import priority
    # Use the pre-normalized segments if present (from run_segmentation_node)
    segments = state.get("_segments_for_priority") if isinstance(state, dict) else None
    if not segments:
        segments = list((state.get("raw_segments") or {}).values()) if isinstance(state, dict) else []
    if not segments:
        return {}
    prioritized = priority.prioritize(segments)
    # copy raw segments into state as well
    return {
        "final_segment": prioritized.get("final_segment"),
        "confidence": prioritized.get("confidence", 0.0),
        "segment_description": prioritized.get("segment_description", ""),
    }


async def generation_node(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Produce a generation output conditioned on the final segment."""
    from agent.phases.generation import aimessage, safety_agent

    final_segment = state.get("final_segment") if isinstance(state, dict) else None
    user_text = state.get("user_message") if isinstance(state, dict) else ""
    prompt = f"Respond for segment: {final_segment}. Input: {user_text}"
    msg = aimessage.prepare_message(prompt, {"segment": final_segment})
    safety = safety_agent.check_safety(msg)
    return {"generation_output": {"message": msg, "safety": safety}}


async def experimentation_node(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Assign experiments/variants and process feedback (placeholder)."""
    from agent.phases.experimentation import selector

    variants = ["A", "B"]
    assigned = selector.select_variant({"segment": state.get("final_segment")}, variants)
    return {"experiment_assignment": {"variant": assigned}}


async def deployment_node(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Deploy selected variant or record deployment metadata (placeholder)."""
    from agent.phases.deployment import deployer

    variant = (state.get("experiment_assignment") or {}).get("variant") if isinstance(state, dict) else "default"
    status = deployer.deploy(version=str(variant), target="staging")
    return {"deployment_status": status}


# Compose the graph with nodes and edges
graph = (
    StateGraph(State, context_schema=Context)
    .add_node(start_node)
    .add_node(goal_router_node)
    .add_node(run_segmentation_node)
    .add_node(priority_node)
    .add_node(generation_node)
    .add_node(experimentation_node)
    .add_node(deployment_node)
    .add_edge("__start__", "start_node")
    .add_edge("start_node", "goal_router_node")
    .add_edge("goal_router_node", "run_segmentation_node")
    .add_edge("run_segmentation_node", "priority_node")
    .add_edge("priority_node", "generation_node")
    .add_edge("generation_node", "experimentation_node")
    .add_edge("experimentation_node", "deployment_node")
    .compile(name="EchoVoice Agent Graph")
)
