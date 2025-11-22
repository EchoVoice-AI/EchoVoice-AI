# Hybrid Semantic Search Migration: FAISS → Azure Cognitive Search

This guide walks through replacing the local FAISS vector store with Azure Cognitive Search (now called Azure AI Search), which provides hybrid search (keyword + semantic) capabilities.

## Why migrate?

- **Production-ready**: Azure Search handles scale, reliability, and backups.
- **Hybrid search**: Combines BM25 (keyword) + semantic ranking for better recall and precision.
- **Semantic re-ranking**: Uses LLMs to re-rank results, improving relevance.
- **No local index**: Eliminates need to rebuild and cache embeddings locally.

## Prerequisites

1. **Azure AI Search resource** — create one in Azure Portal or via Azure CLI:
   ```bash
   az search service create \
     --name my-search-service \
     --resource-group my-rg \
     --sku standard
   ```

2. **Azure OpenAI** — embeddings and optional semantic ranking model

3. **Python packages**:
   ```bash
   pip install azure-search-documents azure-identity
   ```

## Implementation steps

### 1. Set up Azure Search Index

Create an index with fields for hybrid search:

```python
# backend/services/azure_search_setup.py
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
)

def create_search_index(index_name: str, search_client: SearchIndexClient):
    """Create an index with hybrid search fields."""
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="title", type=SearchFieldDataType.String),
        SearchableField(name="section", type=SearchFieldDataType.String),
        SearchableField(name="text", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
        SimpleField(name="url", type=SearchFieldDataType.String),
        SimpleField(name="published_date", type=SearchFieldDataType.String),
        SimpleField(name="source", type=SearchFieldDataType.String),
        # Embedding field for semantic search
        SearchField(
            name="text_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,  # Azure OpenAI embedding dimension
            vector_search_profile_name="myHnsw",
        ),
    ]
    
    index = SearchIndex(name=index_name, fields=fields)
    search_client.create_index(index)
    print(f"Index '{index_name}' created successfully.")
```

### 2. Replace vector_db.py

Create a new implementation using Azure Search:

```python
# backend/services/vector_db.py (updated)
import os
from typing import List, Optional
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.identity import DefaultAzureCredential
from langchain_openai import AzureOpenAIEmbeddings
from langchain_core.documents import Document

# Azure Search configuration
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX", "echvoice-index")

def get_search_client() -> SearchClient:
    """Create Azure Search client."""
    if AZURE_SEARCH_KEY:
        return SearchClient(
            endpoint=AZURE_SEARCH_ENDPOINT,
            index_name=AZURE_SEARCH_INDEX,
            credential=AzureSearchKeyCredential(AZURE_SEARCH_KEY),
        )
    else:
        # Use DefaultAzureCredential (requires MSI/managed identity setup)
        return SearchClient(
            endpoint=AZURE_SEARCH_ENDPOINT,
            index_name=AZURE_SEARCH_INDEX,
            credential=DefaultAzureCredential(),
        )

def get_embedding_model():
    """Get Azure OpenAI embeddings client."""
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT")

    if not endpoint or not api_key or not embedding_deployment:
        raise ValueError(
            "Azure OpenAI configuration missing for embeddings. "
            "Set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, "
            "AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT."
        )

    return AzureOpenAIEmbeddings(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=api_version,
        azure_deployment=embedding_deployment,
    )

def similarity_search(
    query: str,
    k: int = 5,
    hybrid: bool = True,
    semantic: bool = True,
) -> List[Document]:
    """
    Run hybrid search with optional semantic re-ranking.
    
    Args:
        query: search query string
        k: number of results to return
        hybrid: use BM25 + vector search (True) or only vector (False)
        semantic: apply semantic re-ranking (requires Azure Search Premium)
    
    Returns:
        List of LangChain Documents
    """
    if not query:
        return []

    search_client = get_search_client()
    embeddings = get_embedding_model()

    # Generate embedding for the query
    query_vector = embeddings.embed_query(query)

    if hybrid:
        # Hybrid search: keyword (BM25) + vector
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
        # Pure vector search
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

    documents: List[Document] = []
    for result in results:
        doc = Document(
            page_content=result["text"],
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

    return documents
```

### 3. Environment configuration

Add to `.env.template` and `.env`:

```env
# Azure Search
AZURE_SEARCH_ENDPOINT=https://<service-name>.search.windows.net
AZURE_SEARCH_KEY=<admin-key>
AZURE_SEARCH_INDEX=echvoice-index

# Azure OpenAI (for embeddings)
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=<key>
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=text-embedding-3-small
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### 4. Index corpus into Azure Search

Script to upload documents:

```python
# backend/scripts/index_corpus_to_azure.py
import json
import os
from pathlib import Path
from azure.search.documents import SearchClient
from azure.search.documents.models import IndexDocumentsBatch
from azure.identity import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from langchain_openai import AzureOpenAIEmbeddings

def index_corpus(jsonl_path: str, index_name: str):
    """Load JSONL corpus and upload to Azure Search with embeddings."""
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    key = os.getenv("AZURE_SEARCH_KEY")
    
    search_client = SearchClient(
        endpoint=endpoint,
        index_name=index_name,
        credential=AzureKeyCredential(key),
    )
    
    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT"),
    )

    documents = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            doc = json.loads(line)
            
            # Generate embedding for the text
            text_vector = embeddings.embed_query(doc.get("text", ""))
            
            doc["text_vector"] = text_vector
            documents.append(doc)

    # Batch upload
    batch = IndexDocumentsBatch()
    batch.add_upload_actions(documents)
    search_client.index_documents(batch)
    print(f"Indexed {len(documents)} documents to '{index_name}'")

if __name__ == "__main__":
    index_corpus(
        jsonl_path="data/irs_tax_knowledge.jsonl",
        index_name="echvoice-index",
    )
```

Run it:
```bash
cd backend
python scripts/index_corpus_to_azure.py
```

### 5. Update retriever agent

The retriever agent remains compatible since it still gets back `List[Document]`:

```python
# backend/agents/retriever.py remains mostly the same
# Just update the import:
from services.vector_db import similarity_search

# Call remains the same:
docs = similarity_search(query=query_text, k=5, hybrid=True, semantic=True)
```


## Migration checklist

- [ ] Create Azure AI Search resource
- [ ] Set environment variables
- [ ] Run index creation script
- [ ] Upload corpus to Azure Search
- [ ] Update `backend/services/vector_db.py`
- [ ] Test `similarity_search` with hybrid queries
- [ ] Run integration tests to verify end-to-end flow
- [ ] Deploy to production
- [ ] **Verify fallback works:** Simulate Azure Search outage and confirm FAISS fallback triggers

## Fallback mechanism: Azure Search → FAISS

The retriever agent now includes a robust fallback mechanism:

- **Primary:** Azure Cognitive Search is used for all retrievals if available and configured.
- **Automatic fallback:** If Azure Search is unavailable, misconfigured, or returns an error, the system automatically falls back to the local FAISS vector store (no manual intervention required).
- **No code changes needed:** The agent interface and pipeline remain unchanged; fallback is handled internally.

**How it works:**

```python
from services.vector_db import similarity_search as faiss_similarity_search
try:
    from services.vector_db_azure_search import similarity_search as azure_similarity_search
except ImportError:
    azure_similarity_search = None

def retrieve_citations(...):
    ...
    docs = []
    if azure_similarity_search is not None:
        try:
            docs = azure_similarity_search(query=query, k=top_k)
        except Exception as e:
            # Fallback to FAISS
            docs = faiss_similarity_search(query=query, k=top_k, jsonl_path=path)
    else:
        docs = faiss_similarity_search(query=query, k=top_k, jsonl_path=path)
    ...
```

**Testing the fallback:**

1. Unset or misconfigure your Azure Search environment variables, or stop the Azure Search service.
2. Run a retrieval query. The system should print a warning and use FAISS automatically.
3. Restore Azure Search configuration to resume hybrid search.

**Note:** This ensures your RAG pipeline is resilient to cloud outages or misconfiguration, and can always serve results from the local index if needed.

## Performance tips

1. **Semantic configuration**: Enable only for critical queries (adds latency).
2. **Vector search profile tuning**: Adjust `m` and `efSearch` parameters for HNSW algorithm.
3. **Partition strategy**: Partition by source or use query filters for faster lookups.
4. **Caching**: Cache embeddings of frequent queries in Redis.

## References

- [Azure AI Search Python SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/search-documents-readme?view=azure-python)
- [Hybrid search in Azure Search](https://learn.microsoft.com/en-us/azure/search/hybrid-search-how-to-query)
- [Semantic search in Azure Search](https://learn.microsoft.com/en-us/azure/search/semantic-search-overview)
