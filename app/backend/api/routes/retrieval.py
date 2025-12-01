from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Any, Dict

from backend.config import CONFIG_ASK_APPROACH, CONFIG_SEARCH_CLIENT, CONFIG_OPENAI_CLIENT

from PersonalizeAI.nodes.phase2_retrieval import (
    contextual_query_generator,
    vector_search_retriever,
    relevance_grader,
    citation_formatter,
    self_correction,
)

router = APIRouter()


class Phase2Request(BaseModel):
    campaign_goal: str
    segment_description: str


@router.post("/retrieval/run", tags=["Retrieval"])
async def run_retrieval(request: Request, body: Phase2Request) -> Dict[str, Any]:
    """Orchestrate Phase 2 retrieval using services from the running FastAPI app.

    Strategy:
    - Prefer using the configured `CONFIG_ASK_APPROACH` if present (it exposes
      embedding + search helpers).
    - Fallback to the simple node implementations in `PersonalizeAI.nodes.phase2_retrieval`.
    """
    app_cfg = request.app.state.config
    approach = app_cfg.get(CONFIG_ASK_APPROACH)

    # Initialize GraphState-like dict
    state: Dict[str, Any] = {
        "campaign_goal": body.campaign_goal,
        "segment_description": body.segment_description,
    }

    # 1) Generate context query
    cq_update = contextual_query_generator.contextual_query_generator(state)
    state.update(cq_update)

    # 2) Retrieve content (prefer approach utilities)
    if approach is not None:
        # Use approach to compute embedding and run search so it respects configuration
        try:
            vec_query = await approach.compute_text_embedding(state["context_query"])
            docs = await approach.search(
                top=5,
                query_text=state["context_query"],
                filter=None,
                vectors=[vec_query],
                use_text_search=False,
                use_vector_search=True,
                use_semantic_ranker=False,
                use_semantic_captions=False,
            )
            # Map Document dataclass to simple retrieved_content shape
            retrieved = []
            for d in docs:
                retrieved.append({"text": d.content or "", "source_id": d.sourcepage or d.id or ""})
            state["retrieved_content"] = retrieved
        except Exception:
            # Fallback to simulated retriever
            state.update(vector_search_retriever.vector_search_retriever(state))
    else:
        # No approach configured; use local simulated retriever node
        state.update(vector_search_retriever.vector_search_retriever(state))

    # 3) Relevance grading and optional self-correction loop
    next_node = relevance_grader.relevance_grader(state)
    attempts = 0
    while next_node == "SELF_CORRECTION" and attempts < 3:
        attempts += 1
        # Run self-correction using the OpenAI client if available
        openai_client = request.app.state.config.get(CONFIG_OPENAI_CLIENT)
        sc_update = {}
        try:
            prompt_manager = request.app.state.config.get("PROMPT_MANAGER")
            sc_update = await self_correction.self_correction(state, openai_client, prompt_manager=prompt_manager, approach=approach)
        except Exception:
            # Ensure we always have a conservative fallback
            sc_update = {"context_query": (state.get("context_query", "") + " detailed product facts")}

        # Merge returned updates (including audit)
        state.update(sc_update)

        # Re-run retriever using approach if available
        if approach is not None:
            try:
                vec_query = await approach.compute_text_embedding(state["context_query"])
                docs = await approach.search(
                    top=5,
                    query_text=state["context_query"],
                    filter=None,
                    vectors=[vec_query],
                    use_text_search=False,
                    use_vector_search=True,
                    use_semantic_ranker=False,
                    use_semantic_captions=False,
                )
                retrieved = [{"text": d.content or "", "source_id": d.sourcepage or d.id or ""} for d in docs]
                state["retrieved_content"] = retrieved
            except Exception:
                state.update(vector_search_retriever.vector_search_retriever(state))
        else:
            state.update(vector_search_retriever.vector_search_retriever(state))

        next_node = relevance_grader.relevance_grader(state)

    # 4) Citation formatting (finalize)
    signal = citation_formatter.citation_formatter(state)

    return {"status": "success", "phase": "phase2", "signal": signal, "state": state}
