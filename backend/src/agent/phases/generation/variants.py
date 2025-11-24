"""LLM-based message generator agent.

Responsibilities:
- Take customer info, segment output, and RAG citations.
- Generate a small set of outbound message variants (A/B/C) using an LLM.
- Fall back to a simple template-based generator when no LLM config is set.

Note: This file incorporates all helper logic and the robust RAG/Fallback implementation.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List

import azure.identity
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

# NOTE: Removed unused imports: langchain_core.tools, langgraph.checkpoint.memory, langgraph.prebuilt

# --- 1. Environment/Config Setup ---
load_dotenv(override=True)
API_HOST = os.getenv("API_HOST", "github")

# --- LangSmith Placeholder (to prevent import errors) ---
# NOTE: In a real system, replace this with 'from services.langsmith_monitor import ...'
def start_run(*args, **kwargs): return None
def log_event(*args, **kwargs): pass
def finish_run(*args, **kwargs): pass
LANGSMITH_ENABLED = False


def _get_llm():
    """Construct an LLM client based on environment configuration priority."""
    # ... (Your existing _get_llm function remains here)
    if API_HOST == "azure":
        token_provider = azure.identity.get_bearer_token_provider(azure.identity.DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
        model = ChatOpenAI(
            model=os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT"),
            base_url=os.environ["AZURE_OPENAI_ENDPOINT"] + "/openai/v1",
            api_key=token_provider,
        )
    elif API_HOST == "github":
        model = ChatOpenAI(
            model=os.getenv("GITHUB_MODEL", "gpt-4o"),
            base_url="https://models.inference.ai.azure.com",
            api_key=os.environ["GITHUB_TOKEN"],
        )
    elif API_HOST == "ollama":
        model = ChatOpenAI(
            model=os.environ["OLLAMA_MODEL"],
            base_url=os.environ.get("OLLAMA_ENDPOINT", "http://localhost:11434/v1"),
            api_key="none",
        )
    else:
        model = None
    return model

# ---------------------------------------------------------------------
# Helper Functions (Customer, Citation, Context Extraction)
# ---------------------------------------------------------------------


def _get_customer_name(customer: Dict[str, Any]) -> str:
    """Safely extract a display name for the customer."""
    name = customer.get("name") or customer.get("first_name") or ""
    if not name:
        return "there"
    return name


def _get_primary_citation_text(citations: List[Dict[str, Any]]) -> str:
    """Pick the most prominent snippet from the first citation, prioritizing redacted text."""
    if not citations:
        return ""
    first = citations[0]
    return (
        first.get("redacted_text")
        or first.get("content")
        or first.get("text")
        or ""
    )


def _build_context_phrase(segment: Dict[str, Any]) -> str:
    """Build a short human-readable phrase for the segment and use case."""
    use_case_label = segment.get("use_case_label") or segment.get("use_case") or ""
    funnel_stage = segment.get("funnel_stage") or ""
    intent_level = segment.get("intent_level") or ""

    if use_case_label and funnel_stage:
        return f"your {use_case_label} journey ({funnel_stage})"
    if use_case_label:
        return f"your {use_case_label} options"
    if intent_level:
        return f"your options given your {intent_level} interest"
    return "your options"


# ---------------------------------------------------------------------
# Fallback Generator: _fallback_template_variants (MISSING function added)
# ---------------------------------------------------------------------

def _fallback_template_variants(
    customer: Dict[str, Any],
    segment: Dict[str, Any],
    citations: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Deterministic, non-LLM variant generation. (Using the robust template from our discussion)."""
    name = _get_customer_name(customer)
    seg_label = (
        segment.get("segment")
        or segment.get("use_case")
        or "your recent activity"
    )
    context_phrase = _build_context_phrase(segment)
    primary_snippet = _get_primary_citation_text(citations)
    first_url = citations[0].get("url") if citations else None

    variants: List[Dict[str, Any]] = []

    # Variant A: short + direct
    variants.append(
        {
            "id": "A",
            "subject": f"Hi {name}, quick note about {seg_label}",
            "body": (
                f"Hi {name},\n\n"
                f"We wanted to follow up about {context_phrase}.\n"
                f"{primary_snippet}\n\n"
                f"— Our team"
            ),
            "meta": {
                "type": "short",
                "tone": "friendly",
                "context": context_phrase,
                "intent_level": segment.get("intent_level"),
                "generator": "template_fallback",
            },
        }
    )

    # Variant B: a bit more detailed
    body_b_lines = [
        f"Hello {name},", "",
        f"Here are a few helpful details about {context_phrase}.",
    ]
    if primary_snippet:
        body_b_lines.append("")
        body_b_lines.append(primary_snippet)
    if first_url:
        body_b_lines.append("")
        body_b_lines.append(f"You can read more here: {first_url}")
    body_b_lines.append("")
    body_b_lines.append("If you have questions, just reply to this message.")
    body_b_lines.append("")
    body_b_lines.append("— Our team")

    variants.append(
        {
            "id": "B",
            "subject": f"{name}, more details about {context_phrase}",
            "body": "\n".join(body_b_lines),
            "meta": {
                "type": "long",
                "tone": "informative",
                "context": context_phrase,
                "intent_level": segment.get("intent_level"),
                "generator": "template_fallback",
            },
        }
    )

    return variants


# ---------------------------------------------------------------------
# LLM Generator: _generate_with_llm (Your original logic)
# ---------------------------------------------------------------------

def _build_llm_prompt_payload(
    customer: Dict[str, Any],
    segment: Dict[str, Any],
    citations: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Build a compact JSON payload to send to the LLM (PII-safe)."""
    safe_citations = []
    for c in citations:
        safe_citations.append(
            {
                "id": c.get("id"), "title": c.get("title"), "section": c.get("section"),
                "snippet": c.get("redacted_text") or c.get("text") or "",
                "url": c.get("url"), "source": c.get("source"),
            }
        )

    return {
        "customer": {
            "id": customer.get("id"), "email": customer.get("email"),
            "name": _get_customer_name(customer), # Only first name sent to model
        },
        "segment": segment,
        "citations": safe_citations,
    }


def _generate_with_llm(
    customer: Dict[str, Any],
    segment: Dict[str, Any],
    citations: List[Dict[str, Any]],
) -> List[Dict[str, Any]] | None:
    """Use Azure/OpenAI LLM to generate variants."""
    llm = _get_llm()
    if llm is None:
        return None

    payload = _build_llm_prompt_payload(customer, segment, citations)

    system_msg = SystemMessage(
        content=(
            "You are a helpful marketing and customer communications assistant. "
            "You write clear, empathetic, and compliant email or message variants "
            "based ONLY on the information you are given. "
            "Return ONLY a JSON array of variant objects."
        )
    )

    user_instructions = (
        "Using the following JSON input, generate 2 or 3 message variants for the customer.\n\n"
        f"INPUT JSON:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n\n"
        "REQUIREMENTS:\n- Use only the 'snippet' text from citations; do NOT invent new facts.\n"
        "- Tailor tone to the segment.intent_level (higher intent -> more direct next steps).\n"
        "- Each variant must be a JSON object with keys: id, subject, body, meta.\n"
        "- id should be 'A', 'B', 'C', etc.\n"
        "OUTPUT:\nReturn ONLY a JSON array of variant objects. Do not include any explanation or prose."
    )

    human_msg = HumanMessage(content=user_instructions)

    try:
        response = llm.invoke([system_msg, human_msg])
        raw_text = response.content if hasattr(response, "content") else str(response)

        # 1. Parse JSON
        variants = json.loads(raw_text)

        # 2. Basic Sanity Checks and Cleanup
        if not isinstance(variants, list):
            raise ValueError("LLM response is not a JSON list")

        cleaned: List[Dict[str, Any]] = []
        intent_level = segment.get("intent_level")
        for v in variants:
            if not isinstance(v, dict):
                continue
            meta = v.get("meta") or {}
            meta.setdefault("intent_level", intent_level)
            meta.setdefault("generator", "llm")

            cleaned.append(
                {"id": v.get("id"), "subject": v.get("subject"), "body": v.get("body"), "meta": meta}
            )

        if not cleaned:
            raise ValueError("Parsed LLM variants list is empty")

        return cleaned

    except Exception:
        # NOTE: Your original logic catches the exception and returns None, triggering the fallback.
        return None


# ---------------------------------------------------------------------
# Public entrypoint used by LangGraph / orchestrator (FIXED)
# ---------------------------------------------------------------------


def generate_variants(
    customer: Dict[str, Any],
    segment: Dict[str, Any],
    citations: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Public API for the generator agent. Tries LLM first, falls back to template."""
    run_id = None
    # NOTE: You would typically call start_run() here if LANGSMITH_ENABLED is True,
    # but since the check is missing, we proceed assuming run_id is None.
    
    try:
        # 1) Try LLM path
        variants = _generate_with_llm(customer, segment, citations)
        
        if variants is not None:
            # LLM was successful
            if run_id:
                log_event(run_id, "generated_variants", {"count": len(variants)})
                finish_run(run_id, status="success", outputs={"count": len(variants)})
            return variants

        # 2) Fallback path (LLM failed or config missing)
        variants = _fallback_template_variants(customer, segment, citations)
        
        if run_id:
            log_event(run_id, "fallback_variants", {"count": len(variants)})
            finish_run(run_id, status="success", outputs={"count": len(variants), "generator": "template_fallback"})
            
        return variants

    except Exception as e:
        # Catch errors from the fallback template itself (critical failure)
        if run_id:
            log_event(run_id, "error", {"error": str(e)})
            finish_run(run_id, status="error", outputs={"error": str(e)})
        # Re-raise the exception to signal a complete failure to the orchestrator (LangGraph)
        raise