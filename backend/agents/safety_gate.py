"""
Safety gate agent.

Responsibilities:
- Inspect generated message variants from generator.py.
- Block variants that contain:
    - Disallowed / high-risk claims (e.g., "guarantee of cure").
    - Potential PII (detected via simple local patterns and, optionally,
      Azure Content Safety / Content Moderator).
- Return a structured result separating `safe` and `blocked` variants.

Output shape:
{
    "safe": [
        { ...variant... },
        ...
    ],
    "blocked": [
        {
            "variant": { ...variant... },
            "reasons": ["prohibited_term:guarantee of cure", "pii:email"]
        },
        ...
    ]
}
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import os
import re

from services.logger import get_logger
from app.config import LOG_LEVEL   

logger = get_logger("agent.safety")

# --------------------------------------------------------------------
# Basic rule-based checks
# --------------------------------------------------------------------

# Phrases you NEVER want to appear in outbound content.
# Adjust this list to match TRA / client compliance rules.
PROHIBITED_TERMS = [
    "100% guarantee you will save",
    "100% guaranteed to save money",
    "guaranteed lowest price",
    "we guarantee you will love it",
    "guaranteed approval",
    "approved for everyone",
    "no interest ever",
    "0% interest forever",
    "free for life",
]


# Simple PII-like patterns (local fallback, not a full PII system)
EMAIL_REGEX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_REGEX = re.compile(r"\b(?:\+?\d[\d\-\s]{7,}\d)\b")  # crude phone pattern


def _check_prohibited_terms(text: str) -> List[str]:
    """Return list of prohibited terms found in the text."""
    text_low = text.lower()
    hits: List[str] = []
    for term in PROHIBITED_TERMS:
        if term.lower() in text_low:
            hits.append(term)
    return hits


def _check_local_pii(text: str) -> List[str]:
    """
    Very simple local PII detection.

    Returns a list of flags such as:
        ["pii:email", "pii:phone"]
    """
    reasons: List[str] = []

    if EMAIL_REGEX.search(text):
        reasons.append("pii:email")

    if PHONE_REGEX.search(text):
        reasons.append("pii:phone")

    return reasons


# --------------------------------------------------------------------
# Optional: Azure Content Safety / Content Moderator integration
# --------------------------------------------------------------------

# To use Azure AI Content Safety,
# set these in your environment or app.config:
#
#   AZURE_CONTENT_SAFETY_ENDPOINT
#   AZURE_CONTENT_SAFETY_KEY
#
# and install:
#   pip install azure-ai-contentsafety
#
# This code is written so that if the SDK or env vars are missing,
# the agent will quietly skip cloud checks and only use local rules.

try:
    from azure.ai.contentsafety import ContentSafetyClient
    from azure.core.credentials import AzureKeyCredential  # type: ignore

    _HAS_AZURE_SAFETY_SDK = True
except ImportError:
    ContentSafetyClient = None  # type: ignore
    AzureKeyCredential = None  # type: ignore
    _HAS_AZURE_SAFETY_SDK = False


def _get_azure_safety_client() -> Optional[Any]:
    """
    Initialize Azure Content Safety client if configuration is present.

    Returns:
        ContentSafetyClient instance or None if config/SDK is missing.
    """
    if not _HAS_AZURE_SAFETY_SDK:
        return None

    endpoint = os.getenv("AZURE_CONTENT_SAFETY_ENDPOINT")
    key = os.getenv("AZURE_CONTENT_SAFETY_KEY")

    if not endpoint or not key:
        return None

    try:
        client = ContentSafetyClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        return client
    except Exception:
        logger.exception("Failed to initialize Azure Content Safety client.")
        return None


def _check_with_azure_safety(client: Any, text: str) -> List[str]:
    """
    Use Azure Content Safety to scan text.

    This is a placeholder – adjust to your chosen categories/policies.
    Returns a list of reason strings such as:
        ["azure:pii_detected", "azure:content_violation"]
    """
    reasons: List[str] = []

    if not client or not text.strip():
        return reasons

    try:
        # NOTE: The exact API shape may differ slightly depending on
        # the SDK version. Adjust this call once your Azure setup is live.
        #
        # Example pseudo-call:
        #
        # from azure.ai.contentsafety.models import AnalyzeTextOptions
        # request = AnalyzeTextOptions(text=text)
        # response = client.analyze_text(request)
        #
        # Then inspect response.categories, response.pii, etc.

        # For now, we just log that we *would* call Azure here.
        # Replace this block with real logic once Content Safety is configured.
        logger.debug("Azure Content Safety check would run here.")
        # Example placeholder:
        # if response contains PII:
        #     reasons.append("azure:pii_detected")
        # if response flagged policy violations above a threshold:
        #     reasons.append("azure:content_violation")

    except Exception:
        logger.exception("Azure Content Safety check failed; skipping cloud-based safety.")
    return reasons


# Cache client so we don't re-create every time
_AZURE_SAFETY_CLIENT: Optional[Any] = None
if _HAS_AZURE_SAFETY_SDK:
    _AZURE_SAFETY_CLIENT = _get_azure_safety_client()


# --------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------

def safety_check_and_filter(variants: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Run safety checks on a list of variants.

    Each variant is expected to have at least:
        {
          "id": "A",
          "subject": "...",
          "body": "...",
          "meta": { ... }
        }

    Returns:
        {
          "safe": [variant, ...],
          "blocked": [
            {
              "variant": variant,
              "reasons": ["prohibited_term:...", "pii:email", ...]
            },
            ...
          ]
        }
    """
    # Opt-in instrumentation
    try:
        from services.langsmith_monitor import start_run, log_event, finish_run, LANGSMITH_ENABLED
    except Exception:
        start_run = log_event = finish_run = lambda *a, **k: None
        LANGSMITH_ENABLED = False

    run_id = None
    if LANGSMITH_ENABLED:
        run_id = start_run("safety_gate.safety_check_and_filter", {"variant_count": len(variants)})

    safe: List[Dict[str, Any]] = []
    blocked: List[Dict[str, Any]] = []

    for v in variants or []:
        body = v.get("body", "") or ""
        text = f"{v.get('subject', '')}\n{body}"

        reasons: List[str] = []

        # 1) Prohibited terms / false promises
        prohibited_hits = _check_prohibited_terms(text)
        for term in prohibited_hits:
            reasons.append(f"prohibited_term:{term}")

        # 2) Local PII patterns
        reasons.extend(_check_local_pii(text))

        # 3) Optional Azure safety check
        if _AZURE_SAFETY_CLIENT is not None:
            reasons.extend(_check_with_azure_safety(_AZURE_SAFETY_CLIENT, text))

        if reasons:
            blocked.append({"variant": v, "reasons": reasons})
        else:
            safe.append(v)

    result = {"safe": safe, "blocked": blocked}
    logger.info("safety_check_and_filter: safe=%d blocked=%d", len(safe), len(blocked))

    if run_id:
        try:
            log_event(run_id, "safety_result", {"safe": len(safe), "blocked": len(blocked)})
            finish_run(run_id, status="success", outputs={"safe": len(safe), "blocked": len(blocked)})
        except Exception:
            try:
                finish_run(run_id, status="error", outputs={})
            except Exception:
                pass

    return result


# --------------------------------------------------------------------
# Manual test runner
# --------------------------------------------------------------------

if __name__ == "__main__":
    """
    Quick manual test.

    Run from project root with:
        cd backend
        python -m agents.safety_gate

    If AZURE_CONTENT_SAFETY_ENDPOINT and AZURE_CONTENT_SAFETY_KEY
    are set and azure-ai-contentsafety is installed, Azure checks will
    also run. Otherwise, only local rules (prohibited terms + regex PII)
    are applied.
    """
    demo_variants = [
        {
            "id": "A",
            "subject": "Hi Selvi, quick note about payment_plans:StartedFormOrFlow",
            "body": (
                "Hi Selvi,\n\n"
                "We wanted to follow up about your Payment Plans journey (StartedFormOrFlow).\n"
                "A long-term installment plan is designed for larger orders where customers "
                "need several months to pay. Monthly payments are fixed, and setup fees may apply. "
                "This option makes high-cost items more manageable.\n\n"
                "— Our team"
            ),
            "meta": {
                "type": "short",
                "tone": "friendly",
                "context": "your Payment Plans journey (StartedFormOrFlow)",
                "intent_level": "medium",
                "generator": "template_fallback",
            },
        },
        {
            "id": "B",
            "subject": "We guarantee your payment plan will be approved",
            "body": (
                "Hello Selvi,\n\n"
                "We guarantee your payment plan will be approved and we will cure all your Finance problems.\n"
                "Contact us at selvi@example.com or +1 555 123 4567.\n\n"
                "— Risky Team"
            ),
            "meta": {
                "type": "long",
                "tone": "aggressive",
                "context": "non-compliant example",
                "intent_level": "high",
                "generator": "template_fallback",
            },
        },
    ]

    out = safety_check_and_filter(demo_variants)
    from pprint import pprint

    print("\n=== SAFETY RESULT ===")
    pprint(out)
