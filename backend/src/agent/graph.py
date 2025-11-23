"""LangGraph single-node graph template.

Returns a predefined response. Replace logic and configuration as needed.
"""

from __future__ import annotations

from typing import Any, Dict, List
from .state import GraphState

from langgraph.graph import StateGraph
from langgraph.runtime import Runtime
from typing_extensions import TypedDict


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
    from .phases.segmentation import router as segmentation_router

    text = state.get("user_message") if isinstance(state, dict) else ""
    selected = segmentation_router.route_goal({"text": text})
    return {"raw_segments": {selected: {"note": "routed"}}, "_selected_segment": selected}


async def run_segmentation_node(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Run the segmentation modules and collect raw outputs."""
    from .phases.segmentation import rfm, intent, behavioral, profile

    selected = state.get("_selected_segment") if isinstance(state, dict) else None
    outputs = {}
    # Run all modules (they are lightweight) but mark selected
    text = state.get("user_message") if isinstance(state, dict) else ""
    outputs["rfm"] = rfm.segment_rfm({"text": text})
    outputs["intent"] = intent.segment_intent({"text": text})
    outputs["behavioral"] = behavioral.segment_behavioral({"text": text})
    outputs["profile"] = profile.segment_profile({"text": text})

    return {"raw_segments": outputs}


async def priority_node(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Merge segmentation outputs and choose the final prioritized segment."""
    from .phases.segmentation import priority

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
    from .phases.generation import aimessage, safety_agent

    final_segment = state.get("final_segment") if isinstance(state, dict) else None
    user_text = state.get("user_message") if isinstance(state, dict) else ""
    prompt = f"Respond for segment: {final_segment}. Input: {user_text}"
    msg = aimessage.prepare_message(prompt, {"segment": final_segment})
    safety = safety_agent.check_safety(msg)
    return {"generation_output": {"message": msg, "safety": safety}}


async def experimentation_node(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Assign experiments/variants and process feedback (placeholder)."""
    from .phases.experimentation import selector

    variants = ["A", "B"]
    assigned = selector.select_variant({"segment": state.get("final_segment")}, variants)
    return {"experiment_assignment": {"variant": assigned}}


async def deployment_node(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Deploy selected variant or record deployment metadata (placeholder)."""
    from .phases.deployment import deployer

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
