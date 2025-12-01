# backend/services/vector_db_azure_search.py

"""
Azure Cognitive Search (AI Search) adapter for hybrid semantic search.

Replaces local FAISS with a managed Azure Search service that supports:
- Hybrid search (BM25 keyword + vector semantic)
- Semantic re-ranking using LLMs
- Scale and reliability for production

This module provides a drop-in replacement for the original FAISS-based vector_db.py
with the same interface: similarity_search(query, k) -> List[Document]

Environment variables required:
  - AZURE_SEARCH_ENDPOINT: https://<service>.search.windows.net
  - AZURE_SEARCH_KEY: Admin or query key
  - AZURE_SEARCH_INDEX: Index name (default: echvoice-index)
  - AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT: For embeddings
"""

import os
import logging
from typing import List, Optional

from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.identity import DefaultAzureCredential, AzureKeyCredential
from langchain_openai import AzureOpenAIEmbeddings
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# Azure Search configuration
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX", "echvoice-index")

# Caching
_SEARCH_CLIENT: Optional[SearchClient] = None
_EMBEDDING_MODEL: Optional[AzureOpenAIEmbeddings] = None


def get_search_client() -> SearchClient:
    """
    Get or create an Azure Search client.
    
    Uses either key-based auth (if AZURE_SEARCH_KEY is set) or
    DefaultAzureCredential (MSI/managed identity).
    """
    global _SEARCH_CLIENT
    
    if _SEARCH_CLIENT is not None:
        return _SEARCH_CLIENT

    if not AZURE_SEARCH_ENDPOINT:
        raise ValueError(
            "AZURE_SEARCH_ENDPOINT environment variable not set. "
            "Cannot initialize Azure Search client."
        )

    if AZURE_SEARCH_KEY:
        credential = AzureKeyCredential(AZURE_SEARCH_KEY)
        logger.info("Using key-based authentication for Azure Search.")
    else:
        credential = DefaultAzureCredential()
        logger.info("Using DefaultAzureCredential (MSI/managed identity) for Azure Search.")

    _SEARCH_CLIENT = SearchClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        index_name=AZURE_SEARCH_INDEX,
        credential=credential,
    )
    
    return _SEARCH_CLIENT


def get_embedding_model() -> AzureOpenAIEmbeddings:
    """
    Get or create an Azure OpenAI embeddings client.
    
    Raises ValueError if required config is missing.
    """
    global _EMBEDDING_MODEL
    
    if _EMBEDDING_MODEL is not None:
        return _EMBEDDING_MODEL

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT")

    if not endpoint or not api_key or not embedding_deployment:
        raise ValueError(
            "Azure OpenAI configuration missing for embeddings. "
            "Set: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, "
            "AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT"
        )

    _EMBEDDING_MODEL = AzureOpenAIEmbeddings(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=api_version,
        azure_deployment=embedding_deployment,
    )
    
    return _EMBEDDING_MODEL


def similarity_search(
    query: str,
    k: int = 5,
    hybrid: bool = True,
    semantic: bool = False,
) -> List[Document]:
    """
    Run a hybrid semantic search against the Azure Search index.
    
    Args:
        query: Search query string.
        k: Number of results to return (top k).
        hybrid: If True, combines BM25 (keyword) + vector search.
                If False, uses vector search only.
        semantic: If True, apply semantic re-ranking (requires Premium tier).
    
    Returns:
        List of LangChain Documents with page_content and metadata.
        Metadata includes: id, title, section, url, published_date, source, score, rerank_score.
    
    Raises:
        ValueError: If required environment variables are not set.
        Exception: If Azure Search request fails.
    """
    if not query:
        logger.debug("Empty query provided, returning empty results.")
        return []

    try:
        search_client = get_search_client()
        embeddings = get_embedding_model()

        # Generate embedding for the query
        logger.debug(f"Generating embedding for query: {query[:100]}")
        query_vector = embeddings.embed_query(query)

        # Build search request
        if hybrid:
            logger.debug("Using hybrid search (BM25 + vector).")
            results = search_client.search(
                search_text=query,
                vector_queries=[
                    VectorizedQuery(
                        vector=query_vector,
                        k_nearest_neighbors=k,
                        fields="text_vector",
                    ),
                ],
                semantic_configuration_name="default" if semantic else None,
                query_type="semantic" if semantic else "full",
                query_language="en-us" if semantic else None,
                top=k,
            )
        else:
            logger.debug("Using pure vector search.")
            results = search_client.search(
                vector_queries=[
                    VectorizedQuery(
                        vector=query_vector,
                        k_nearest_neighbors=k,
                        fields="text_vector",
                    ),
                ],
                top=k,
            )

        # Convert results to LangChain Documents
        documents: List[Document] = []
        for result in results:
            doc = Document(
                page_content=result.get("text", ""),
                metadata={
                    "id": result.get("id"),
                    "title": result.get("title"),
                    "section": result.get("section"),
                    "url": result.get("url"),
                    "published_date": result.get("published_date"),
                    "source": result.get("source", "azure_search"),
                    "score": result.get("@search.score"),
                    "rerank_score": result.get("@search.reranker_score"),
                },
            )
            documents.append(doc)

        logger.info(
            f"Search returned {len(documents)} results for query: {query[:50]}"
        )
        return documents

    except Exception as e:
        logger.error(f"Azure Search query failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    """
    Quick manual test for Azure Search retrieval.

    Run with:
        cd backend
        python -m services.vector_db_azure_search
    
    Make sure AZURE_SEARCH_ENDPOINT and other env vars are set.
    """
    try:
        print("Testing Azure Search retrieval...")
        results = similarity_search(
            query="payment plan options if I cannot pay in full",
            k=3,
            hybrid=True,
            semantic=False,
        )
        
        for i, doc in enumerate(results, start=1):
            print("-" * 60)
            print(f"Result #{i}")
            print("ID:     ", doc.metadata.get("id"))
            print("Title:  ", doc.metadata.get("title"))
            print("Score:  ", doc.metadata.get("score"))
            print("Text:   ", doc.page_content[:200], "...")
            
    except Exception as e:
        print(f"Error: {e}")
