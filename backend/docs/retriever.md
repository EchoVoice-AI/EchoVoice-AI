# Retriever Agent

This document describes the retriever agent implemented in `backend/agents/retriever.py`. It explains purpose, API, behavior, PII handling, examples, configuration, and extension points so the agent can be safely used in RAG (retrieval-augmented generation) flows.

Location
- backend/agents/retriever.py

Purpose
- Turn user/segment context into a search query, run a similarity search against the local corpus (or vector DB), redact obvious PII, and return a list of citation objects suitable for downstream LLM generation.

High-level responsibilities
- Accept a segmentation/intent result (segment_result) provided by the segmenter.
- Build a concise query that reflects the user's intent and funnel stage.
- Call the shared vector DB service (`services.vector_db.similarity_search`) to find top-k similar documents.
- Apply basic PII redaction before any text is passed to the LLM.
- Return structured citation objects with both original and redacted text plus useful metadata.

API / Contract

- Function
  - `retrieve_citations(segment_result: Dict[str, Any], top_k: int = 5, jsonl_path: Optional[str] = None) -> List[Dict[str, Any]]`

- Input
  - `segment_result`: dict produced by the segmenter. Common keys used:
    - `use_case` or `use_case_label` (e.g. `"payment_plans"`, `"Payment Plans"`)
    - `funnel_stage` (e.g. `"StartedFormOrFlow"`)
    - `intent_level` (e.g. `"low"|"medium"|"high"`)
    - `reasons`: list of reason strings (first element is used)
  - `top_k`: number of results to return (default 5)
  - `jsonl_path`: optional path to the corpus JSONL file, overrides `DEFAULT_JSONL_PATH`

- Output
  - A list of citation dictionaries with the following shape:
    {
      "id": str | None,
      "title": str | None,
      "section": str | None,
      "text": str,            # original document text
      "redacted_text": str,   # PII-safe version to present to LLM
      "url": str | None,
      "published_date": str | None,
      "source": str,          # e.g. "tax_irs" or "corpus"
    }

Behavior and implementation notes

1. Query construction
- `build_query_from_segment(segment_result)` converts the segment_result into a compact text query.
- It uses the following fields (if available) to build the query:
  - use_case_label / use_case
  - funnel_stage
  - "intent: {intent_level}"
  - the first element of `reasons`
- Parts are joined with " | " to form the query string. If segment_result is empty, a fallback string ("help options and next steps") is used.

2. Similarity search
- The retriever delegates to `services.vector_db.similarity_search(query, k, jsonl_path)` to get ranking results.
- Default corpus path: `DEFAULT_JSONL_PATH` (imported from `services.vector_db`).
- Each returned document is expected to be an object with `.page_content` and `.metadata` attributes (typical of vector search + document wrapper patterns).

3. PII redaction
- `redact_pii(text)` performs simple regex-based redaction of:
  - email addresses -> "[REDACTED_EMAIL]"
  - US-style phone numbers (with optional +1 and common separators) -> "[REDACTED_PHONE]"
  - SSN-like patterns (###-##-####) -> "[REDACTED_SSN]"
- Limitations:
  - This is intentionally simple and conservative. It will not detect all PII (e.g., names, addresses, international phone formats, tax IDs other than SSN pattern).
  - Regexes can produce false positives or miss edge-cases. Do not rely on this as the only privacy control for sensitive corpora in production.
  - Consider integrating a dedicated PII detection service for stronger guarantees.

4. Output assembly
- For each search result document:
  - original text = `doc.page_content` (or "")
  - redacted text = result of `redact_pii(original_text)`
  - metadata fields are pulled from `doc.metadata` (id, title, section, url, published_date, source)
  - the returned `source` defaults to `"corpus"` if not provided in metadata

Usage / Examples

- Typical function call:

```py
from agents.retriever import retrieve_citations

segment = {
    "use_case": "payment_plans",
    "use_case_label": "Payment Plans",
    "funnel_stage": "StartedFormOrFlow",
    "intent_level": "medium",
    "reasons": ["interested in: Payment Plans", "started form but did not finish"],
}

citations = retrieve_citations(segment, top_k=3)
for c in citations:
    print("Title:", c["title"])
    print("URL:", c["url"])
    print("Redacted:", c["redacted_text"][:200], "...")
```

- Sample returned item (illustrative):

```json
{
  "id": "doc_123",
  "title": "How Payment Plans Work",
  "section": "Overview",
  "text": "If you owe money you can call 555-123-4567 or email debt@example.com to...",
  "redacted_text": "If you owe money you can call [REDACTED_PHONE] or email [REDACTED_EMAIL] to...",
  "url": "https://docs.example.com/payment-plans",
  "published_date": "2024-06-01",
  "source": "corpus"
}
```

Manual test runner
- The module includes a `__main__` block so it can be run directly for quick checks:

    cd backend
    python -m agents.retriever

- The runner:
  - builds a sample segment_result
  - prints the DEFAULT_JSONL_PATH in use
  - calls `retrieve_citations(..., top_k=3)` and prints top matches and their redacted text

Configuration and environment
- The retriever uses `services.vector_db` for similarity search. In the scaffold this is a simple local lookup; for production, replace the implementation with a vector DB (Pinecone, Weaviate, Milvus, Azure Vector DB, etc.) or an embeddings+index service.
- Use `jsonl_path` to override the default corpus location for testing or staging.

Security and privacy recommendations
- Do not treat regex redaction as a comprehensive PII protection — add additional safeguards:
  - Apply redaction and filtering closer to the ingestion pipeline to avoid storing raw PII when possible.
  - Log only metadata or redacted text when persisting LLM inputs/outputs.
  - Consider applying data classification / allowlist rules to the corpus.
  - For high-sensitivity domains, route RAG retrievals through a separate, audited service with strict access control.

Extensibility
- Swap vector search backend:
  - Keep the same `similarity_search(query, k, jsonl_path)` signature or wrap the new client with a small adapter so the retriever code remains unchanged.
- Improve query construction:
  - `build_query_from_segment` is intentionally simple and domain-neutral. If you have domain signals (product id, taxonomy, synonyms), enrich the query builder or synthesize multiple queries per segment.
- Enhance PII detection:
  - Replace `redact_pii` with a call to a PII detection service or use an NLP model to detect and mask named entities, account numbers, etc.
- Add scoring/thresholds:
  - Allow filtering results below a similarity threshold or expose similarity score alongside returned citations.

Troubleshooting
- If `similarity_search` returns no documents:
  - Verify `DEFAULT_JSONL_PATH` points to an indexed corpus.
  - Confirm embeddings/index were created for the corpus.
  - Try increasing `top_k` or adjusting the query by inspecting `build_query_from_segment` output.
- If PII is being missed:
  - Add or refine regexes, or plug in a stronger PII detection pipeline.
- If documents are too large for the LLM:
  - Truncate `redacted_text` or chunk long documents at ingestion and store section-level metadata.

Testing
- Unit tests should cover:
  - Query building with various segment_result shapes.
  - PII redaction on representative text examples.
  - Integration test that stubs `similarity_search` and validates the final citation shape.
- For manual verification, use the __main__ runner described above.

Changelog / Notes
- The current implementation is built for clarity and local testing. For production use:
  - Replace the simple vector lookup with a robust vector DB and add monitoring/metrics.
  - Harden PII detection and auditing using Azure Content Moderator.

---

I've created this documentation explaining the retriever's responsibilities, API, PII behavior, examples, and extension points so the module is easier to use and maintain. Next, if you'd like, I can open a PR that replaces the existing backend/docs/retriever.md with this file, or I can generate unit test stubs for the query builder and redaction functions — tell me which you'd prefer.
