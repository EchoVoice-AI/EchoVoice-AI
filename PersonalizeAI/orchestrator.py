"""
Simple async orchestrator that ties Phases 3 and 4 together.

This module intentionally keeps orchestration lightweight and defensive:
- It uses Phase 3 nodes (generation + compliance loop) when available.
- It then runs Phase 4 experimentation nodes to pick a winner and produce
  a feedback payload and a deployment queue entry.

Usage:
    from PersonalizeAI.orchestrator import run_full_pipeline
    import asyncio

    state = { 'segment_description': 'High value shoppers', 'campaign_goal': 'Reduce churn', 'retrieved_content': [...] }
    asyncio.run(run_full_pipeline(state, openai_client=..., prompt_manager=..., approach=...))

"""
from typing import Any, Dict, Optional
import inspect


async def run_full_pipeline(state: Dict[str, Any], openai_client: Optional[Any] = None, prompt_manager: Optional[Any] = None, approach: Optional[Any] = None) -> Dict[str, Any]:
    """Run a full pipeline: Phase 3 generation+compliance followed by Phase 4 experimentation.

    The function mutates and returns `state`.
    """
    # Lazy imports to avoid heavy startup costs and to be robust in tests
    try:
        from PersonalizeAI.nodes.phase3_generation.ai_message_generator import ai_message_generator
        from PersonalizeAI.nodes.phase3_generation.compliance_agent import compliance_agent
        from PersonalizeAI.nodes.phase3_generation.rewrite_decision import rewrite_decision
        from PersonalizeAI.nodes.phase3_generation.automated_rewrite import automated_rewrite
    except Exception:
        ai_message_generator = compliance_agent = rewrite_decision = automated_rewrite = None

    try:
        from PersonalizeAI.nodes.phase4_experimentation.abn_experiment_simulator import abn_experiment_simulator
        from PersonalizeAI.nodes.phase4_experimentation.winning_variant_selector import winning_variant_selector
        from PersonalizeAI.nodes.phase4_experimentation.deployment_router import deployment_router
        from PersonalizeAI.nodes.phase4_experimentation.feedback_processor import feedback_processor
    except Exception:
        abn_experiment_simulator = winning_variant_selector = deployment_router = feedback_processor = None

    # Ensure some defaults
    state.setdefault("segment_description", "")
    state.setdefault("campaign_goal", "")
    state.setdefault("retrieved_content", [])

    # Helper to call both sync and async node functions with flexible kwargs
    async def _call_node(fn, _state, **kwargs):
        if fn is None:
            return None
        try:
            if inspect.iscoroutinefunction(fn):
                try:
                    return await fn(_state, **kwargs)
                except TypeError:
                    return await fn(_state)
            else:
                try:
                    return fn(_state, **kwargs)
                except TypeError:
                    return fn(_state)
        except Exception as exc:  # defensive: don't let one node break entire pipeline
            print(f"Orchestrator: node {getattr(fn, '__name__', str(fn))} raised: {exc}")
            return None

    # --- Phase 1: Segmentation (optional) ---
    # If a Phase 1 segmentation module exists, try to use it; otherwise use a small fallback.
    try:
        import importlib
        phase1_mod = importlib.import_module("PersonalizeAI.nodes.phase1_segmentation.segmenter")
    except Exception:
        phase1_mod = None

    if phase1_mod is not None:
        seg_fn = None
        for candidate in ("segment", "segmenter", "generate_segment_description"):
            if hasattr(phase1_mod, candidate):
                seg_fn = getattr(phase1_mod, candidate)
                break
        if seg_fn is not None:
            seg_update = await _call_node(seg_fn, state, openai_client=openai_client, prompt_manager=prompt_manager, approach=approach)
            if isinstance(seg_update, dict):
                state.update(seg_update)
    else:
        # Fallback: if no segment_description, derive a simple one from existing fields
        if not state.get("segment_description"):
            if state.get("campaign_goal"):
                state["segment_description"] = f"segment_for_{state.get('campaign_goal')[:40]}"
            else:
                state["segment_description"] = "general_audience"
            print(f"Orchestrator: using fallback segmentation -> {state['segment_description']}")

    # --- Phase 2: Retrieval (contextual query -> vector search -> relevance -> correction/citation) ---
    try:
        from PersonalizeAI.nodes.phase2_retrieval.contextual_query_generator import contextual_query_generator
        from PersonalizeAI.nodes.phase2_retrieval.vector_search_retriever import vector_search_retriever
        from PersonalizeAI.nodes.phase2_retrieval.relevance_grader import relevance_grader
        from PersonalizeAI.nodes.phase2_retrieval.self_correction import self_correction
        from PersonalizeAI.nodes.phase2_retrieval.citation_formatter import citation_formatter
    except Exception:
        contextual_query_generator = vector_search_retriever = relevance_grader = self_correction = citation_formatter = None

    # Contextual query
    if contextual_query_generator is not None:
        cq_update = await _call_node(contextual_query_generator, state, openai_client=openai_client, prompt_manager=prompt_manager, approach=approach)
        if isinstance(cq_update, dict):
            state.update(cq_update)

    # Vector retrieval
    if vector_search_retriever is not None:
        vs_update = await _call_node(vector_search_retriever, state, openai_client=openai_client, prompt_manager=prompt_manager, approach=approach)
        if isinstance(vs_update, dict):
            state.update(vs_update)

    # Relevance grading -> either SELF_CORRECTION or CITATION_FORMATTER
    if relevance_grader is not None:
        try:
            route = relevance_grader(state)
        except TypeError:
            # some graders might be async
            route = await _call_node(relevance_grader, state)
        if route == "SELF_CORRECTION" and self_correction is not None:
            sc_update = await _call_node(self_correction, state, openai_client=openai_client, prompt_manager=prompt_manager, approach=approach)
            if isinstance(sc_update, dict):
                state.update(sc_update)
        else:
            # default to citation formatter if available
            if citation_formatter is not None:
                cf_update = citation_formatter(state)
                if isinstance(cf_update, dict):
                    state.update(cf_update)

    # Phase 3: Generation + Compliance
    if ai_message_generator is not None:
        gen_update = await ai_message_generator(state, openai_client=openai_client, prompt_manager=prompt_manager, approach=approach)
        state.update(gen_update or {})
    else:
        # No generator available; ensure message_variants exists
        state.setdefault("message_variants", [])

    # Compliance loop
    if compliance_agent is not None and rewrite_decision is not None and automated_rewrite is not None:
        max_iter = 3
        iter_count = 0
        while True:
            iter_count += 1
            comp_update = await compliance_agent(state, openai_client=openai_client, prompt_manager=prompt_manager, approach=approach)
            state.update(comp_update or {})
            route = rewrite_decision(state)
            if route == "END_PHASE_3" or iter_count >= max_iter:
                break
            rewrite_update = await automated_rewrite(state, openai_client=openai_client, prompt_manager=prompt_manager, approach=approach)
            state.update(rewrite_update or {})

    # Phase 4: Experimentation & Feedback
    if abn_experiment_simulator is not None:
        perf_update = abn_experiment_simulator(state)
        state.update(perf_update or {})

    if winning_variant_selector is not None:
        win_update = winning_variant_selector(state)
        state.update(win_update or {})

    # Deployment router: concurrently send to feedback processor and deployment queue
    if deployment_router is not None:
        exits = deployment_router(state)
        # Feedback
        if "FEEDBACK_LOOP" in exits and feedback_processor is not None:
            feedback_processor(state)
        # Deployment queue: simulate by appending to state['deployment_queue']
        if "DEPLOYMENT_QUEUE" in exits:
            dq = state.setdefault("deployment_queue", [])
            winner = state.get("winning_variant_id")
            if winner:
                dq.append({"variant_id": winner, "timestamp": __import__("datetime").datetime.utcnow().isoformat()})

    return state
