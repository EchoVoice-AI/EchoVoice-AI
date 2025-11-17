"""GitHub Models embeddings adapter.

This module provides a small wrapper that calls the GitHub Models inference
endpoint via the Azure `azure.ai.inference` SDK (the GitHub Models endpoint
uses the same API surface). It implements the minimal interface expected by
the rest of the project: `embed_documents` and `embed_query` which return a
list of float vectors.

If `azure.ai.inference` is not installed or the environment variables are not
set, this module will raise ImportError when attempting to construct the
client — callers should handle that and fall back to `FakeEmbeddings`.
"""
from typing import List, Optional
import os

try:
    from azure.ai.inference import EmbeddingsClient
    from azure.core.credentials import AzureKeyCredential
except Exception:  # pragma: no cover - import-time fallback
    EmbeddingsClient = None  # type: ignore
    AzureKeyCredential = None  # type: ignore


class GitHubEmbeddings:
    """Simple wrapper for GitHub Models embeddings via `EmbeddingsClient`.

    Usage:
        client = GitHubEmbeddings(endpoint, token, model_name)
        vectors = client.embed_documents(["text1", "text2"])
    """

    def __init__(self, endpoint: str, token: str, model: str):
        if EmbeddingsClient is None or AzureKeyCredential is None:
            raise ImportError(
                "azure-ai-inference is required for GitHubEmbeddings."
            )
        if not endpoint or not token or not model:
            raise ValueError("endpoint, token and model must be provided")

        self._client = EmbeddingsClient(endpoint=endpoint, credential=AzureKeyCredential(token))
        self._model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        # The client returns an object with `.data` elements, each having `.embedding`.
        response = self._client.embed(input=texts, model=self._model)
        return [item.embedding for item in response.data]

    def embed_query(self, text: str) -> List[float]:
        resp = self._client.embed(input=[text], model=self._model)
        return resp.data[0].embedding

    def __call__(self, texts):
        """Callable compatibility: accept a single string or list of strings.

        LangChain's FAISS implementation sometimes calls the embeddings
        object as a function. Providing __call__ keeps compatibility by
        routing to embed_query or embed_documents accordingly.
        """
        # Single string -> embed_query
        if isinstance(texts, str):
            return self.embed_query(texts)

        # If it's an iterator/generator, convert to list
        try:
            # Treat bytes as scalar, guard against that
            if isinstance(texts, (bytes, bytearray)):
                return self.embed_query(texts.decode("utf-8"))
        except Exception:
            pass

        # Otherwise assume sequence of strings
        return self.embed_documents(list(texts))

    # Provide a small compatibility layer for LangChain-style usage:
    # LangChain's FAISS.from_documents expects an `embed_documents` method.
