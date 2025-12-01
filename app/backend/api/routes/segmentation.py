from fastapi import APIRouter
from pydantic import BaseModel
import sys
from pathlib import Path
from typing import Any

# Ensure the repository root is on sys.path so PersonalizeAI is importable when
# the backend runs from `app/backend` working directory.
ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PersonalizeAI.state import GraphState  # type: ignore
from PersonalizeAI.nodes.phase1_segmentation import goal_router as goal_router_module  # type: ignore

router = APIRouter()


class Phase1Request(BaseModel):
    campaign_goal: str
    user_message: str


@router.post("/segmentor/run", tags=["Segmentation"])
async def run_segmentation(request: Phase1Request) -> Any:
    """Run a simple Phase 1 segmentation flow using the PersonalizeAI nodes.

    The flow:
    - create initial GraphState with inputs
    - call goal_router to pick a segmentation node
    - call the chosen segmenter node
    - call priority_output to finalize the selection
    - return final_segment, confidence, description
    """
    # Initialize minimal GraphState
    state: GraphState = {
        "campaign_goal": request.campaign_goal,
        "user_message": request.user_message,
    }

    # Determine which segmenter to run
    next_node = goal_router_module.goal_router(state)

    # Map node ids to implementation modules
    node_map = {
        "RFM_SEGMENTATION": "PersonalizeAI.nodes.phase1_segmentation.rfm_segmenter",
        "INTENT_SEGMENTATION": "PersonalizeAI.nodes.phase1_segmentation.intent_segmenter",
        "BEHAVIORAL_SEGMENTATION": "PersonalizeAI.nodes.phase1_segmentation.behavioral_segmenter",
        "PROFILE_SEGMENTATION": "PersonalizeAI.nodes.phase1_segmentation.profile_segmenter",
    }

    segment_module_name = node_map.get(next_node)
    if not segment_module_name:
        return {"status": "error", "message": "No segmenter found for node: %s" % next_node}

    # Import and run the segmenter
    try:
        seg_mod = __import__(segment_module_name, fromlist=["*"])
        state = seg_mod.run(state)  # each module exposes run(state)
    except Exception as exc:  # pragma: no cover - simple runtime guard
        return {"status": "error", "message": f"Segmenter failed: {exc}"}

    # Run priority_output to choose final segment (best-effort)
    try:
        prio_mod = __import__("PersonalizeAI.nodes.phase1_segmentation.priority_output", fromlist=["*"])
        state = prio_mod.run(state)
    except Exception:
        # If priority_output is missing or errors, continue with whatever state has
        pass

    return {
        "status": "success",
        "final_segment": state.get("final_segment"),
        "confidence": state.get("confidence"),
        "segment_description": state.get("segment_description"),
        "raw_state": state,
    }