# Generator Agent

This document describes the generator agent implemented at `backend/agents/generator.py`. It explains purpose, behavior, inputs/outputs, configuration, and usage examples so developers and integrators can understand how message variants are produced.

## Purpose

Generate personalized outbound message variants (A/B/C) for customers using:
- Segment data (who the customer is and why they are being contacted).
- RAG citations (retrieved documents/snippets to ground claims).
- An LLM when available (Azure OpenAI or OpenAI).
- A deterministic template fallback when no LLM is configured so local testing works without secrets.

The generator is designed to produce short, structured results suitable for downstream safety checks, rendering, or A/B testing.

## Location

- File: `backend/agents/generator.py`

## Public API / Contract

- Function: `generate_variants(customer: dict, segment: dict, citations: list) -> list[dict]`

Inputs:
- `customer` (dict): customer identity metadata. Typical keys: `id`, `email`, `name`, `first_name`.
- `segment` (dict): segment output (from the segmenter/orchestrator). Typical keys: `segment`, `use_case`, `use_case_label`, `funnel_stage`, `intent_level`, `reasons`.
- `citations` (list[dict]): list of retrieval results (from retriever) that include redacted or safe text fields (e.g., `redacted_text`, `text`, `content`), `title`, `url`, `source`, etc.

Output:
- A list of variant objects, each with the structure:
  {
    "id": str,           # "A", "B", "C", ...
    "subject": str,
    "body": str,
    "meta": {            # meta must include: type (short/medium/long), tone, intent_level
      "type": str,
      "tone": str,
      "intent_level": str,
      ...other meta...
    }
  }

Example usage:
```py
from agents.generator import generate_variants

variants = generate_variants(customer, segment, citations)
# -> [ { 'id': 'A', 'subject': '...', 'body': '...', 'meta': {...} }, ... ]
```

## High-level behavior

1. Attempt LLM generation if an LLM client can be constructed from environment/config:
   - Priority: Azure Chat (Azure OpenAI) -> OpenAI (non-Azure).
   - When used, the agent builds a compact JSON payload (redacted citation snippets only) and sends it with a SystemMessage + HumanMessage prompt. The agent expects the LLM to return a JSON array of variant objects (no prose).
   - Minimal validation and sanitization are applied to the returned JSON; if parsing fails or response invalid, the function falls back to template generation.

2. If no LLM is configured or LLM generation fails, a deterministic template fallback produces 2 variants (A and B) using simple string templates. This ensures the system remains testable in local/dev without secrets.

## Important internal helpers (what they do)

- _get_customer_name(customer) -> str
  - Safely extracts a display name to address the recipient. Falls back to "there".

- _get_primary_citation_text(citations) -> str
  - Returns the most prominent snippet for use in templates, preferring `redacted_text`, then `content`, then `text`.

- _build_context_phrase(segment) -> str
  - Builds a short human-readable phrase representing the use case and funnel stage (examples: "your Payment Plans journey (CompletedScheduledStep)", "your Payment Plans options", "your options given your very_high interest").

- _build_llm_prompt_payload(customer, segment, citations) -> dict
  - Constructs a compact payload sent to the LLM. Important: it sends only safe citation fields and uses `redacted_text` (or fallback) as `snippet`. This reduces PII leakage.

## LLM configuration and behavior

LLM selection logic:
- Azure: chosen when the following config values are present:
  - AZURE_OPENAI_ENDPOINT
  - AZURE_OPENAI_API_KEY
  - AZURE_OPENAI_CHAT_DEPLOYMENT
  - (Optional) AZURE_OPENAI_API_VERSION (default used if missing)
  - Uses `langchain_openai.AzureChatOpenAI(...)` with temperature=0.7 and max_tokens=512.
- OpenAI (non-Azure): chosen when OPENAI_API_KEY is present. Defaults model to `OPENAI_MODEL_NAME` or `"gpt-4o-mini"` if not set. Uses `langchain_openai.ChatOpenAI(...)` with temperature=0.7 and max_tokens=512.
- If neither config is present, `_get_llm()` returns `None`.

LLM Prompt & Expected Output:
- The system message instructs the model to behave as a helpful marketing/customer communications assistant and to only use provided info.
- The user message contains the compact INPUT JSON and strict REQUIREMENTS:
  - Use only the citation `snippet` text; do not invent legal/tax or factual claims.
  - Be honest and use non-guaranteeing language ("may", "can help", not "will definitely").
  - Match tone to `segment.intent_level`.
  - Output must be a JSON array of objects with keys: `id`, `subject`, `body`, `meta`.
  - `meta` must include `type` (short/medium/long), `tone`, and `intent_level`.
  - The agent returns ONLY the JSON array in the LLM reply (no extra prose).
- The code calls `llm.invoke([system_msg, human_msg])` and expects the result content to be JSON. The code attempts to parse the returned text with `json.loads()` and performs basic sanity checking.

Validation & fallback:
- The code verifies the parsed JSON is a list of dicts and ensures `meta.intent_level` is set (propagates from `segment` if missing).
- If parsing fails or validation indicates an empty result, the LLM path returns `None` and the generator falls back to the template generator.
- Errors are printed (in production, wire this to a proper logger).

## Template fallback (non-LLM)

When no LLM config exists or LLM generation fails, `_fallback_template_variants(...)` returns deterministic variants:

Variant A (short + direct)
- subject: e.g., "Hi Selvi, quick note about payment_plans:CompletedScheduledStep"
- body: short note including the primary citation snippet and a sign-off.
- meta includes type "short", tone "friendly", and generator "template_fallback".

Variant B (longer + informative)
- subject: e.g., "Selvi, more details about your Payment Plans journey (CompletedScheduledStep)"
- body: longer text including snippet and optionally the first citation URL.
- meta includes type "long", tone "informative", and generator "template_fallback".

This fallback is deterministic and safe for local testing.

## JSON payload shape sent to the LLM

The LLM receives a compact JSON payload (example):
```json
{
  "customer": {
    "id": "U001",
    "email": "selvi@example.com",
    "name": "Selvi"
  },
  "segment": {
    "segment": "payment_plans:CompletedScheduledStep",
    "use_case": "payment_plans",
    "use_case_label": "Payment Plans",
    "funnel_stage": "CompletedScheduledStep",
    "intent_level": "very_high",
    "reasons": [
      "interested in: Payment Plans",
      "completed a scheduled step (call/session/meeting)",
      "shows very strong commitment"
    ]
  },
  "citations": [
    {
      "id": "company_services#consult",
      "title": "Company Services – Consultations",
      "section": "First consultation",
      "snippet": "A licensed professional reviews your information and explains options during the first consultation.",
      "url": "https://example.com/services/consultation",
      "source": "corpus"
    }
  ]
}
```

Notes:
- Citations are reduced to safe fields and include `snippet` which is the redacted text (or fallback).
- Avoid sending full unredacted document text to the LLM to reduce PII leakage.

## Expected LLM response format

The LLM should return ONLY a JSON array of variants, for example:
```json
[
  {
    "id": "A",
    "subject": "Hi Selvi — Quick next steps for Payment Plans",
    "body": "Hi Selvi,\n\nThanks for completing the scheduled step in your Payment Plans journey. A licensed professional reviews your information and explains options during the first consultation.\n\nIf you'd like to move forward, reply here and we can schedule the next step.\n\n— Our team",
    "meta": {
      "type": "short",
      "tone": "friendly",
      "intent_level": "very_high"
    }
  },
  {
    "id": "B",
    "subject": "Selvi — More options tailored to your Payment Plans interest",
    "body": "Hello Selvi,\n\nHere are a few helpful details about your Payment Plans options. A licensed professional reviews your information and explains options during the first consultation.\n\nYou can read more here: https://example.com/services/consultation\n\nIf you have questions, simply reply to this message.\n\n— Our team",
    "meta": {
      "type": "long",
      "tone": "informative",
      "intent_level": "very_high"
    }
  }
]
```

Important:
- The module performs a minimal sanity check; ensure the LLM strictly returns valid JSON. In production consider stronger validation/schemas and a safety review step.

## Security & PII considerations

- The generator prefers `redacted_text` for citations and intentionally restricts the citation field sent to the model to `snippet` (redacted).
- Only the first name (via `_get_customer_name`) is sent to the model to avoid leaking full PII.
- Never send unredacted sensitive fields to the LLM in production.
- The system message instructs the model not to invent facts — nevertheless a downstream safety check should verify claims against the provided citations.

## Environment variables / config used by the agent

- AZURE_OPENAI_ENDPOINT
- AZURE_OPENAI_API_KEY
- AZURE_OPENAI_API_VERSION (optional, default: "2024-02-15-preview" in code)
- AZURE_OPENAI_CHAT_DEPLOYMENT
- OPENAI_API_KEY
- OPENAI_MODEL_NAME (optional, default: "gpt-4o-mini" in code)

The code expects a `app.config` module that exposes the names above. If your config lives elsewhere, adjust the import in `generator.py`.

## Dependencies

- langchain_core (typing & Document)
- langchain_openai (AzureChatOpenAI, ChatOpenAI)
- Python standard libraries: json, typing

Ensure these are included in your `requirements.txt` or dependency management.

## Error handling & logging

- LLM invocation errors or parsing issues are caught in `_generate_with_llm()`; the function prints a message and returns `None`.
- The public `generate_variants()` will then call the template fallback to ensure a deterministic output even when the LLM fails.
- For production, replace `print()` with structured logging and consider:
  - Emitting metrics for LLM errors.
  - Notifying downstream systems when generation falls back to template.
  - Recording provenance (which generator produced each variant) inside `meta.generator`.

## Manual test runner

The module includes a `__main__` section with demo inputs. To run locally:
```
cd backend
python -m agents.generator
```
- If LLM config exists, it will attempt the LLM path.
- Otherwise it will print the template variants.

## Tips for production hardening

- Enforce a JSON schema for returned variants and validate strictly.
- Rate-limit and backoff for LLM calls.
- Ensure audit logs capture the full prompt payload and LLM response (careful with PII — log redacted versions).
- Add a dedicated safety/claims checker that verifies statements against provided citations (e.g., detect hallucinations or claims that are not supported by `snippet` text).
- Consider deterministic variant seeding for A/B testing reproducibility.

## Example: fallback output (from demo run)

Variant structure produced by the template fallback:
```json
[
  {
    "id": "A",
    "subject": "Hi Selvi, quick note about payment_plans:CompletedScheduledStep",
    "body": "Hi Selvi,\n\nWe wanted to follow up about your Payment Plans journey (CompletedScheduledStep).\nA licensed professional reviews your information and explains options during the first consultation.\n\n— Our team",
    "meta": {
      "type": "short",
      "tone": "friendly",
      "context": "your Payment Plans journey (CompletedScheduledStep)",
      "intent_level": "very_high",
      "generator": "template_fallback"
    }
  },
  {
    "id": "B",
    "subject": "Selvi, more details about your Payment Plans journey (CompletedScheduledStep)",
    "body": "Hello Selvi,\n\nHere are a few helpful details about your Payment Plans journey (CompletedScheduledStep).\n\nA licensed professional reviews your information and explains options during the first consultation.\n\nYou can read more here: https://example.com/services/consultation\n\nIf you have questions, just reply to this message.\n\n— Our team",
    "meta": {
      "type": "long",
      "tone": "informative",
      "context": "your Payment Plans journey (CompletedScheduledStep)",
      "intent_level": "very_high",
      "generator": "template_fallback"
    }
  }
]
```

## Summary

- `generate_variants(...)` provides a consistent generator interface for downstream systems.
- It prefers LLM-based generation but falls back to a safe template so developers can run the pipeline without secrets.
- The module is designed to limit PII exposure and to embed citation provenance to enable downstream safety review.

If you want, I can:
- Add a JSON schema file and validate LLM outputs against it.
- Add structured logging (e.g., using the `logging` module) instead of `print`.
- Add unit tests that cover LLM success, LLM parse failures, and the fallback path.
