# backend/agents/generator.py

"""
LLM-based message generator agent.

Responsibilities:
- Take customer info, segment output, and RAG citations.
- Generate a small set of outbound message variants (A/B/C) using an LLM
  when available (Azure OpenAI or OpenAI).
- Fall back to a simple template-based generator when no LLM config is set,
  so developers can still run manual tests locally without .env.

Input:
    customer: dict
    segment: dict
    citations: list[dict]  (from retriever.py, including redacted_text)

Output:
    List of variant dicts, e.g.:
    [
      {
        "id": "A",
        "subject": "...",
        "body": "...",
        "meta": {
          "type": "short",
          "tone": "friendly",
          "intent_level": "very_high"
        }
      },
      ...
    ]
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from langchain_core.documents import Document  # for downstream typing only
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from services.langsmith_monitor import start_run, log_event, finish_run, LANGSMITH_ENABLED

# IMPORTANT: adjust this import path if your config module lives elsewhere.
# You said "app/config.py", so we import from app.config.
from app.config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_CHAT_DEPLOYMENT,
    OPENAI_API_KEY,
    OPENAI_MODEL_NAME,
)


# ---------------------------------------------------------------------
# Helpers: name, snippet, context
# ---------------------------------------------------------------------


def _get_customer_name(customer: Dict[str, Any]) -> str:
    """
    Safely extract a display name for the customer.
    Falls back to a generic term if nothing is provided.
    """
    name = customer.get("name") or customer.get("first_name") or ""
    if not name:
        return "there"
    return name


def _get_primary_citation_text(citations: List[Dict[str, Any]]) -> str:
    """
    Pick the most prominent snippet from the first citation.

    We prefer 'redacted_text' so we don't leak PII to the LLM.
    Then fall back to 'content' or 'text' if needed.
    """
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
    """
    Build a short human-readable phrase for the segment and use case.

    Example:
      "your Payment Plans journey (CompletedScheduledStep)"
      "your Payment Plans options"
    """
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
# LLM configuration
# ---------------------------------------------------------------------


def _has_azure_config() -> bool:
    return bool(
        AZURE_OPENAI_ENDPOINT
        and AZURE_OPENAI_API_KEY
        and AZURE_OPENAI_CHAT_DEPLOYMENT
    )


def _has_openai_config() -> bool:
    return bool(OPENAI_API_KEY)


def _get_llm():
    """
    Construct an LLM client.

    Priority:
    1) Azure OpenAI (chat deployment)
    2) OpenAI (non-Azure) if OPENAI_API_KEY is set
    3) None  -> caller should fall back to template-based generator
    """
    if _has_azure_config():
        # Azure Chat deployment (e.g. "gpt-4o-mini")
        return AzureChatOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION or "2024-02-15-preview",
            azure_deployment=AZURE_OPENAI_CHAT_DEPLOYMENT,
            temperature=0.7,
            max_tokens=512,
        )

    if _has_openai_config():
        # Non-Azure OpenAI model (e.g. "gpt-4o-mini")
        model_name = OPENAI_MODEL_NAME or "gpt-4o-mini"
        return ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model=model_name,
            temperature=0.7,
            max_tokens=512,
        )

    # No LLM config found
    return None


# ---------------------------------------------------------------------
# Template-based fallback (no LLM)
# ---------------------------------------------------------------------


def _fallback_template_variants(
    customer: Dict[str, Any],
    segment: Dict[str, Any],
    citations: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Deterministic, non-LLM variant generation.

    Used when no Azure/OpenAI config is available so developers can
    still test end-to-end without a .env.
    """
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
        f"Hello {name},",
        "",
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
# LLM-based variant generation
# ---------------------------------------------------------------------


def _build_llm_prompt_payload(
    customer: Dict[str, Any],
    segment: Dict[str, Any],
    citations: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Build a compact JSON payload to send to the LLM.

    We only send redacted_text for safety and strip unnecessary fields.
    """
    safe_citations = []
    for c in citations:
        safe_citations.append(
            {
                "id": c.get("id"),
                "title": c.get("title"),
                "section": c.get("section"),
                "snippet": c.get("redacted_text") or c.get("text") or "",
                "url": c.get("url"),
                "source": c.get("source"),
            }
        )

    return {
        "customer": {
            "id": customer.get("id"),
            "email": customer.get("email"),
            # Only send first name to model (no full PII)
            "name": _get_customer_name(customer),
        },
        "segment": segment,
        "citations": safe_citations,
    }


def _generate_with_llm(
    customer: Dict[str, Any],
    segment: Dict[str, Any],
    citations: List[Dict[str, Any]],
) -> Optional[List[Dict[str, Any]]]:
    """
    Use Azure/OpenAI LLM to generate variants.

    Returns:
      - list of variants on success
      - None if something goes wrong (caller will fall back to template)
    """
    llm = _get_llm()
    if llm is None:
        # No LLM config available
        print("[generator] No LLM config found – using template fallback.")
        return None

    payload = _build_llm_prompt_payload(customer, segment, citations)

    system_msg = SystemMessage(
        content=(
            "You are a helpful marketing and customer communications assistant. "
            "You write clear, empathetic, and compliant email or message variants "
            "based ONLY on the information you are given. "
            "Do not invent benefits, guarantees, or facts. "
            "Highlight next steps and options in a friendly, non-pushy way."
        )
    )

    user_instructions = (
        "Using the following JSON input, generate 2 or 3 message variants for the customer.\n\n"
        "INPUT JSON:\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}\n\n"
        "REQUIREMENTS:\n"
        "- Use only the 'snippet' text from citations; do NOT invent new legal or tax claims.\n"
        "- Be honest and non-guaranteeing (e.g., say 'may', 'can help', not 'will definitely').\n"
        "- Tailor tone to the segment.intent_level (higher intent -> more direct next steps).\n"
        "- Each variant must be a JSON object with keys: id, subject, body, meta.\n"
        "- meta must include: type (short/medium/long), tone, and intent_level.\n"
        "- id should be 'A', 'B', 'C', etc.\n\n"
        "OUTPUT:\n"
        "Return ONLY a JSON array of variant objects. Do not include any explanation or prose."
    )

    human_msg = HumanMessage(content=user_instructions)

    try:
        response = llm.invoke([system_msg, human_msg])
        raw_text = response.content if hasattr(response, "content") else str(response)

        # Try to parse as JSON
        variants = json.loads(raw_text)

        # Basic sanity check: list of dicts
        if not isinstance(variants, list):
            raise ValueError("LLM response is not a JSON list")

        cleaned: List[Dict[str, Any]] = []
        intent_level = segment.get("intent_level")
        for v in variants:
            if not isinstance(v, dict):
                continue
            meta = v.get("meta") or {}
            # Ensure intent_level gets propagated
            if "intent_level" not in meta:
                meta["intent_level"] = intent_level
            meta.setdefault("generator", "llm")

            cleaned.append(
                {
                    "id": v.get("id"),
                    "subject": v.get("subject"),
                    "body": v.get("body"),
                    "meta": meta,
                }
            )

        if not cleaned:
            raise ValueError("Parsed LLM variants list is empty")

        return cleaned

    except Exception as e:
        # In production you might log this via logger instead of print
        print(f"[generator] LLM generation failed, falling back to template. Error: {e}")
        return None


# ---------------------------------------------------------------------
# Public entrypoint used by LangGraph / orchestrator
# ---------------------------------------------------------------------


def generate_variants(
    customer: Dict[str, Any],
    segment: Dict[str, Any],
    citations: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Public API for the generator agent.

    - Tries to use an LLM (Azure/OpenAI) when config is available.
    - Falls back to template-based generation when LLM is not configured
      or if an error occurs.

    This keeps your pipeline testable locally even without secrets.
    """
    run_id = None
    if LANGSMITH_ENABLED:
        run_id = start_run("generator.generate_variants", {"agent": "generator", "customer_id": customer.get("id"), "use_case": segment.get("use_case")})

    try:
        # 1) Try LLM path
        variants = _generate_with_llm(customer, segment, citations)
        if variants is not None:
            if run_id:
                log_event(run_id, "generated_variants", {"count": len(variants)})
                finish_run(run_id, status="success", outputs={"count": len(variants)})
            return variants

        # 2) Fallback path (no LLM or error)
        variants = _fallback_template_variants(customer, segment, citations)
        if run_id:
            log_event(run_id, "fallback_variants", {"count": len(variants)})
            finish_run(run_id, status="success", outputs={"count": len(variants), "generator": "template_fallback"})
        return variants

    except Exception as e:
        if run_id:
            log_event(run_id, "error", {"error": str(e)})
            finish_run(run_id, status="error", outputs={"error": str(e)})
        raise


# ---------------------------------------------------------------------
# Manual test runner
# ---------------------------------------------------------------------


if __name__ == "__main__":
    """
    Quick manual test:

        cd backend
        python -m agents.generator

    Behavior:
      - If Azure/OpenAI config is present, uses the LLM to generate variants.
      - If not, uses the template-based fallback generator.
    """
    demo_customer = {
        "id": "U001",
        "email": "selvi@example.com",
        "name": "Selvi",
    }

    demo_segment = {
        "segment": "payment_plans:CompletedScheduledStep",
        "use_case": "payment_plans",
        "use_case_label": "Payment Plans",
        "funnel_stage": "CompletedScheduledStep",
        "intent_level": "very_high",
        "reasons": [
            "interested in: Payment Plans",
            "completed a scheduled step (call/session/meeting)",
            "shows very strong commitment",
        ],
    }

    demo_citations = [
        {
            "id": "company_services#consult",
            "title": "Company Services – Consultations",
            "section": "First consultation",
            "text": "A licensed professional reviews your information and explains options during the first consultation.",
            "redacted_text": "A licensed professional reviews your information and explains options during the first consultation.",
            "url": "https://example.com/services/consultation",
            "published_date": "2025-01-01",
            "source": "corpus",
        }
    ]

    out = generate_variants(demo_customer, demo_segment, demo_citations)
    for v in out:
        print("-" * 60)
        print("Variant ID:", v["id"])
        print("Subject:   ", v["subject"])
        print("Body:\n", v["body"])
        print("Meta:", v["meta"])
