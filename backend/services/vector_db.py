# backend/services/vector_db.py

"""
Vector DB service using LangChain + FAISS + Azure OpenAI embeddings.

Responsibilities:
- Load a JSONL corpus (one JSON object per line)
- Build a FAISS vector store over the "text" field
- Expose a simple similarity_search(query, k) API that returns LangChain Documents

This file is intentionally domain-agnostic:
- It doesn't know about "segments" or "tax" specifically.
- It just assumes each JSON object has:
    - text
    - id, title, section, url, published_date, source (optional but helpful)
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

# Defer optional heavy imports (langchain, FAISS) until runtime so tests and
# the LangGraph smoke runner can import this module without installing
# langchain-related packages.
AzureOpenAIEmbeddings = None
FAISS = None
Document = None
FakeEmbeddings = None
try:
    from langchain_openai import AzureOpenAIEmbeddings  # type: ignore
except Exception:
    AzureOpenAIEmbeddings = None

try:
    from langchain_community.vectorstores import FAISS  # type: ignore
except Exception:
    FAISS = None

try:
    from langchain_core.documents import Document  # type: ignore
except Exception:
    class Document:
        def __init__(self, page_content: str = "", metadata: dict | None = None):
            self.page_content = page_content
            self.metadata = metadata or {}

try:
    from langchain_community.embeddings import FakeEmbeddings  # type: ignore
except Exception:
    FakeEmbeddings = None


# Default JSONL path (can be overridden by callers)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_JSONL_PATH = PROJECT_ROOT / "data" / "irs_tax_knowledge.jsonl"

# Internal cache
_VECTORSTORE: Optional[Any] = None
_CORPUS_CACHE: Optional[List[Dict[str, Any]]] = None


def get_embedding_model():
    """
    Create an Azure OpenAI embeddings client using environment variables.

    For local testing (no .env / no Azure config), we fall back to FakeEmbeddings
    so the pipeline can run without real embeddings. Retrieval quality will be
    meaningless, but structure + wiring can be tested.
    """
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT")

    if not endpoint or not api_key or not embedding_deployment:
        # Dev fallback: don't crash, prefer FakeEmbeddings if available
        print(
            "[vector_db] Azure OpenAI config missing – using FakeEmbeddings (or zero-vector fallback) for local testing."
        )
        # size can be anything consistent; 1536 is a common embedding dimension
        if FakeEmbeddings is not None:
            return FakeEmbeddings(size=1536)

        # Minimal in-memory fallback embedding model: returns zero vectors
        class _ZeroEmbeddings:
            def __init__(self, size: int = 1536):
                self.size = size

            def embed_documents(self, docs):
                return [[0.0] * self.size for _ in docs]

            def embed_query(self, q):
                return [0.0] * self.size

        return _ZeroEmbeddings(size=1536)

    # Real Azure embeddings for production
    return AzureOpenAIEmbeddings(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=api_version,
        azure_deployment=embedding_deployment,
    )



def load_corpus(jsonl_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Load the JSONL corpus (one JSON object per line).
    This is generic and does not assume a specific domain.
    """
    path = Path(jsonl_path) if jsonl_path else DEFAULT_JSONL_PATH
    docs: List[Dict[str, Any]] = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                docs.append(json.loads(line))
            except json.JSONDecodeError:
                # For production: log or raise. For now, skip bad lines.
                continue

    return docs


def _build_vectorstore(jsonl_path: Optional[str] = None) -> Any:
    """
    Build a FAISS vector store from the JSONL corpus.

    Each JSON object becomes a LangChain Document with:
        page_content = text
        metadata     = { id, title, section, url, published_date, source }
    """
    corpus = load_corpus(jsonl_path)

    documents: List[Document] = []
    for d in corpus:
        page_content = d.get("text", "")
        metadata = {
            "id": d.get("id"),
            "title": d.get("title"),
            "section": d.get("section"),
            "url": d.get("url"),
            "published_date": d.get("published_date"),
            # allow caller to override "source"; default to whatever is present or "corpus"
            "source": d.get("source", "corpus"),
        }
        documents.append(Document(page_content=page_content, metadata=metadata))

    embeddings = get_embedding_model()

    # If FAISS is not available, provide a lightweight in-memory placeholder
    if FAISS is None:
        class _InMemoryVS:
            def __init__(self, docs):
                self._docs = docs

            def similarity_search(self, query, k=5):
                # naive: return first k documents as Document instances
                results = []
                for d in self._docs[:k]:
                    results.append(Document(page_content=d.get("text", ""), metadata={k: v for k, v in d.items()}))
                return results

        return _InMemoryVS(corpus)

    vs = FAISS.from_documents(documents, embedding=embeddings)
    return vs


def get_vectorstore(jsonl_path: Optional[str] = None) -> Any:
    """
    Get (or lazily build) the FAISS vector store.
    """
    global _VECTORSTORE, _CORPUS_CACHE

    if _VECTORSTORE is not None:
        return _VECTORSTORE

    _VECTORSTORE = _build_vectorstore(jsonl_path)
    _CORPUS_CACHE = load_corpus(jsonl_path)  # cache raw corpus if needed later
    return _VECTORSTORE


def similarity_search(
    query: str,
    k: int = 5,
    jsonl_path: Optional[str] = None,
) -> List[Document]:
    """
    Run similarity search over the vector store.

    Returns a list of LangChain Documents with .page_content and .metadata.
    """
    if not query:
        return []

    vs = get_vectorstore(jsonl_path)
    return vs.similarity_search(query, k=k)


if __name__ == "__main__":
    """
    Quick manual test for the vector DB service.

        cd backend
        python -m services.vector_db
    """
    print(f"Using corpus: {DEFAULT_JSONL_PATH}")
    vs = get_vectorstore()
    docs = similarity_search("payment plan options if I cannot pay in full", k=3)
    for i, d in enumerate(docs, start=1):
        print("-" * 60)
        print(f"Result #{i}")
        print("ID:     ", d.metadata.get("id"))
        print("Title:  ", d.metadata.get("title"))
        print("Text:   ", d.page_content[:200], "...")
