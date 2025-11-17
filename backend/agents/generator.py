import os
from typing import List, Dict, Any

from app.tracing import tracer

try:
    # Prefer AzureOpenAI if available (project uses Azure in other places),
    # otherwise try standard OpenAI wrapper. These imports are optional so
    # the repo remains runnable without an LLM configured.
    from langchain_openai import AzureOpenAI
except Exception:
    AzureOpenAI = None

try:
    from langchain_openai import OpenAI
except Exception:
    OpenAI = None

# Optional: prefer a concrete GitHub LLM adapter implemented using
# the `azure.ai.inference` SDK. This adapter provides exact constructor
# semantics for the GitHub Models inference endpoint.
try:
    from services.github_llm import GitHubLLM  # type: ignore
except Exception:
    GitHubLLM = None


def _call_llm_for_variants(name: str, seg_label: str, citation_text: str) -> List[Dict[str, Any]]:
    """Example LLM call that attaches the LangSmith tracer via callbacks.

    This function is intentionally defensive: it only runs when an LLM
    class is available and the environment provides the required API key.
    Otherwise it raises or returns an empty list and the caller can fall
    back to deterministic output.
    """
    # Prefer Azure if configured
    try:
        if AzureOpenAI and os.getenv("AZURE_OPENAI_API_KEY"):
            llm = AzureOpenAI(
                azure_deployment=os.getenv("AZURE_OPENAI_COMPLETION_DEPLOYMENT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                callbacks=[tracer] if tracer else None,
            )
        elif OpenAI and os.getenv("OPENAI_API_KEY"):
            llm = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                callbacks=[tracer] if tracer else None,
            )
        elif (
            GitHubLLM
            and os.getenv("GITHUB_TOKEN")
            and (os.getenv("GITHUB_LLM_MODEL") or os.getenv("GITHUB_MODEL"))
        ):
            # Use the GitHubLLM adapter which uses the azure.ai.inference
            # TextGenerationClient under the hood. It does not support
            # LangChain-style `callbacks`, so we instantiate it and call
            # `generate` directly. Tracing (LangSmith) will capture higher-
            # level application events but not the internal SDK calls unless
            # you use LangChain wrappers.
            try:
                model_name = os.getenv("GITHUB_LLM_MODEL") or os.getenv("GITHUB_MODEL")
                github_endpoint = os.getenv(
                    "GITHUB_EMBEDDINGS_ENDPOINT", "https://models.github.ai/inference"
                )
                llm = GitHubLLM(endpoint=github_endpoint, token=os.getenv("GITHUB_TOKEN"), model=model_name)
                # We'll call llm.generate(prompt) below.
            except Exception:
                return []
        else:
            # No LLM configured
            return []

        prompt = (
            f"Create two short email variants (id, subject, body, meta.type) for a user named {name} "
            f"about {seg_label}. Include the citation: {citation_text}\n\nRespond in plain text."
        )

        # Many LangChain LLM wrappers implement __call__ to return text.
        # We wrap in try/except to avoid breaking runtime if the API surface
        # differs in the environment.
        try:
            response = llm(prompt)
            text = str(response)
        except Exception:
            # Best-effort: try generate API
            try:
                res = llm.generate([prompt])
                text = res.generations[0][0].text
            except Exception:
                return []

        # Return a single LLM-derived variant as an example. In production
        # you'd parse structured output (JSON) from the LLM.
        return [
            {
                "id": "LLM-1",
                "subject": f"LLM suggestion about {seg_label}",
                "body": text,
                "meta": {"type": "llm"},
            }
        ]
    except Exception:
        return []


def generate_variants(customer: dict, segment: dict, citations: list) -> list:
    # Produce a few A/B variants using available info (mocked + optional LLM)
    name = customer.get('name', 'Customer')
    seg_label = segment.get('segment') if segment else None
    # Citation shape may vary: some retrievers return 'content', others 'text' or 'redacted_text'.
    citation_text = ''
    if citations:
        first = citations[0]
        citation_text = first.get('content') or first.get('text') or first.get('redacted_text') or ''

    variants: List[Dict[str, Any]] = []

    # Always include simple deterministic A/B variants so tests and local runs
    # continue to work when no LLM is configured.
    variants.append({
        'id': 'A',
        'subject': f"Hi {name}, quick note about {seg_label}",
        'body': f"Hi {name},\n\nWe thought you might like this: {citation_text}\n\n— Team",
        'meta': {'type': 'short'}
    })
    variants.append({
        'id': 'B',
        'subject': f"{name}, more on the Acme plan",
        'body': f"Hello {name},\n\nDetails: {citation_text}\nLearn more on our site.",
        'meta': {'type': 'long'}
    })

    # Try an LLM-derived variant if possible; this demonstrates attaching
    # the LangSmith tracer via callbacks so runs show up in LangSmith.
    llm_variants = _call_llm_for_variants(name, seg_label or 'unknown', citation_text)
    if llm_variants:
        variants.extend(llm_variants)

    return variants
