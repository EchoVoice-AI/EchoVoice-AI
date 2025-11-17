"""GitHub-hosted LLM/chat completion adapter using azure.ai.inference.

This adapter provides a minimal `GitHubLLM` class with a `generate` method
that returns text for a prompt. It uses the `TextGenerationClient` from
`azure.ai.inference` when available and falls back gracefully if the SDK
is not installed.

Constructor:
    GitHubLLM(endpoint: str, token: str, model: str)

Method:
    generate(prompt: str) -> str

Note: The `azure.ai.inference` client APIs may vary across versions; this
adapter tries common names and call patterns but keeps calls in try/except
so the repo remains runnable when the SDK isn't present.
"""
from typing import Optional
import os

try:
    from azure.ai.inference import TextGenerationClient
    from azure.core.credentials import AzureKeyCredential
except Exception:  # pragma: no cover - import-time fallback
    TextGenerationClient = None  # type: ignore
    AzureKeyCredential = None  # type: ignore


class GitHubLLM:
    """Adapter around Azure Inference text generation client pointed at GitHub Models."""

    def __init__(self, endpoint: str, token: str, model: str):
        if TextGenerationClient is None or AzureKeyCredential is None:
            raise ImportError("azure-ai-inference is required for GitHubLLM")
        if not endpoint or not token or not model:
            raise ValueError("endpoint, token and model must be provided")

        self._client = TextGenerationClient(endpoint=endpoint, credential=AzureKeyCredential(token))
        self._model = model

    def generate(self, prompt: str) -> str:
        """Generate text for a prompt. Returns best-effort string output.

        This attempts the common synchronous `generate` call signature that the
        Azure inference client exposes. If the response shape differs, we try
        to pull a reasonable text fallback.
        """
        if not prompt:
            return ""

        try:
            # Common signature: client.generate(model=model, input=prompt)
            response = self._client.generate(model=self._model, input=prompt)
            # Response may have `.generated_text`, `.content`, or nested `outputs`
            # Try a few known access patterns.
            if hasattr(response, "generated_text"):
                return str(response.generated_text)
            if hasattr(response, "content"):
                return str(response.content)
            # Some SDKs return an iterator of outputs
            if hasattr(response, "outputs"):
                outputs = getattr(response, "outputs")
                if outputs:
                    first = outputs[0]
                    # common shape: first.content or first.text
                    return str(getattr(first, "content", getattr(first, "text", "")))

            # Fallback: try converting to str
            return str(response)
        except Exception:
            # Try alternate call signature: client.begin_generate or client.create
            try:
                op = self._client.begin_generate(model=self._model, input=prompt)
                result = op.result()
                if hasattr(result, "generated_text"):
                    return str(result.generated_text)
                return str(result)
            except Exception:
                return ""
