"""Citation Formatter (Phase 2 finalizer).

Cleans, deduplicates, and ensures snippets have `source_id` and `text`.
Returns a signal string 'END_PHASE_2' to denote the phase completion.
"""
from typing import Dict, Any
from PersonalizeAI.state import GraphState


def citation_formatter(state: GraphState) -> str:
    content = state.get("retrieved_content", []) or []

    final_citable_context = []
    seen = set()

    for snippet in content:
        text = snippet.get("text")
        source = snippet.get("source_id")
        if not text or not source:
            continue
        key = (text.strip(), source)
        if key in seen:
            continue
        seen.add(key)
        # Simple formatting: keep text and source, could add citation bracket
        formatted_text = f"{text.strip()} [{source}]"
        final_citable_context.append({"text": formatted_text, "source_id": source})

    state["retrieved_content"] = final_citable_context

    print(f"Phase 2 Complete. Formatted {len(final_citable_context)} citable snippets.")

    return "END_PHASE_2"
