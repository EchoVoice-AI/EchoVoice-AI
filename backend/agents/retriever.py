
# Import both vector DB backends for fallback
from services.vector_db import similarity_search as faiss_similarity_search, DEFAULT_JSONL_PATH
try:
    from services.vector_db_azure_search import similarity_search as azure_similarity_search
except ImportError:
    azure_similarity_search = None


"""
Retriever agent for RAG.

Responsibilities:
- Take segment_result from the segmenter
- Build a search query that reflects user intent and funnel stage
- Call the shared vector_db service to run similarity search
- Apply basic PII redaction BEFORE anything is sent to the LLM
- Return a list of citation dicts suitable for the generator

Output shape:
    [
      {
        "id": ...,
        "title": ...,
        "section": ...,
        "text": ...,            # original text
        "redacted_text": ...,   # PII-safe version for LLM
        "url": ...,
        "published_date": ...,
        "source": "tax_irs" or "corpus",
      },
      ...
    ]
"""

import re
from typing import List, Dict, Any, Optional

from services.vector_db import similarity_search, DEFAULT_JSONL_PATH



# -------------------------------------------------------------------
# PII redaction (basic)
# -------------------------------------------------------------------

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(
    r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b"
)
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def redact_pii(text: str) -> str:
    """
    Very simple PII redaction for:
      - email addresses
      - phone numbers
      - SSN-like patterns

    NOTE: This is not perfect PII detection, but it prevents obvious
    identifiers from being sent to the LLM.
    """
    if not text:
        return text

    text = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    text = PHONE_RE.sub("[REDACTED_PHONE]", text)
    text = SSN_RE.sub("[REDACTED_SSN]", text)
    return text


# -------------------------------------------------------------------
# Helper: build a search query from segment info
# -------------------------------------------------------------------

def build_query_from_segment(segment_result: Dict[str, Any]) -> str:
    """
    Turn the segment info into a text query for RAG.

    Uses:
      - use_case_label (e.g. "Payment Plans")
      - funnel_stage (e.g. "StartedFormOrFlow")
      - intent_level  (e.g. "medium")
      - first reason, if there is one

    This stays fairly domain-neutral: it doesn't hard-code "IRS" or "tax",
    but in practice your corpus is IRS + company policy content.
    """
    if not segment_result:
        return "help options and next steps"

    use_case_label = segment_result.get("use_case_label") or segment_result.get("use_case") or ""
    funnel_stage = segment_result.get("funnel_stage") or ""
    intent_level = segment_result.get("intent_level") or ""
    reasons = segment_result.get("reasons") or []
    first_reason = reasons[0] if reasons else ""

    parts = [
        use_case_label,
        funnel_stage,
        f"intent: {intent_level}",
        first_reason,
    ]

    # Filter out empty strings
    parts = [p for p in parts if p]
    if not parts:
        return "help options and next steps"

    # You can tweak this format anytime; it's just a text query to the embedding space
    return " | ".join(parts)


# -------------------------------------------------------------------
# Main RAG entrypoint for the agent
# -------------------------------------------------------------------


def retrieve_citations(
    segment_result: Dict[str, Any],
    top_k: int = 5,
    jsonl_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve top_k relevant citations based on the segment_result.
    Tries Azure Search first, falls back to FAISS if Azure Search fails or is unavailable.
    """
    query = build_query_from_segment(segment_result)
    path = jsonl_path or str(DEFAULT_JSONL_PATH)

    docs = []
    azure_error = None
    # Try Azure Search first if available
    if azure_similarity_search is not None:
        try:
            docs = azure_similarity_search(query=query, k=top_k)
        except Exception as e:
            azure_error = e
            # Fallback to FAISS
    if not docs:
        docs = faiss_similarity_search(query=query, k=top_k, jsonl_path=path)
        if azure_error:
            print(f"[retriever] Azure Search failed, using FAISS fallback: {azure_error}")

    citations: List[Dict[str, Any]] = []
    for doc in docs:
        meta = doc.metadata or {}
        original_text = doc.page_content or ""
        redacted = redact_pii(original_text)

        citations.append(
            {
                "id": meta.get("id"),
                "title": meta.get("title"),
                "section": meta.get("section"),
                "text": original_text,
                "redacted_text": redacted,
                "url": meta.get("url"),
                "published_date": meta.get("published_date"),
                "source": meta.get("source", "corpus"),
            }
        )

    return citations


# -------------------------------------------------------------------
# Manual test runner
# -------------------------------------------------------------------

if __name__ == "__main__":
    """
    Quick manual test:

        cd backend
        python -m agents.retriever

    This will:
      - run a test query derived from a fake segment_result
      - print the top matches
    """

    seg_example = {
        "use_case": "payment_plans",
        "use_case_label": "Payment Plans",
        "funnel_stage": "StartedFormOrFlow",
        "intent_level": "medium",
        "reasons": ["interested in: Payment Plans", "started form but did not finish"],
    }

    print(f"Using corpus: {DEFAULT_JSONL_PATH}")
    results = retrieve_citations(seg_example, top_k=3)

    for i, c in enumerate(results, start=1):
        print("-" * 60)
        print(f"Result #{i}")
        print("ID:     ", c["id"])
        print("Title:  ", c["title"])
        print("Section:", c["section"])
        print("URL:    ", c["url"])
        print("Text:   ", c["text"][:200], "...")
        print("Redacted text:", c["redacted_text"][:200], "...")
