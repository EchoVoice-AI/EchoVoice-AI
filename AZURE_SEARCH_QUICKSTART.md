# Azure Search Hybrid Semantic Search Implementation Guide

## Overview

This guide provides a complete implementation for replacing the local FAISS vector store with Azure Cognitive Search (Azure AI Search), enabling hybrid semantic search with keyword (BM25) and vector components.

**What you get:**
- Hybrid search: combines keyword matching + semantic vector search
- Semantic re-ranking: uses LLMs to re-rank results for better relevance
- Managed infrastructure: scale, reliability, backups handled by Azure
- Production-ready: no local index building or caching needed

---

## Quick Start

### 1. Prerequisites

**Azure resources:**
- Azure AI Search resource (create in Azure Portal or CLI)
- Azure OpenAI (for embeddings and optional semantic ranking)

**Install packages:**
```bash
cd backend
pip install azure-search-documents azure-identity
```

### 2. Configure environment variables

Add to `.env`:

```env
# Azure Search
AZURE_SEARCH_ENDPOINT=https://<service-name>.search.windows.net
AZURE_SEARCH_KEY=<admin-or-query-key>
AZURE_SEARCH_INDEX=echvoice-index

# Azure OpenAI (for embeddings)
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=<key>
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=text-embedding-3-small
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### 3. Create the search index

```bash
cd backend
python scripts/setup_azure_search_index.py
```

This creates an index with:
- Text fields (title, section, text)
- Vector field (text_vector) with HNSW algorithm
- Semantic search configuration (title + text fields)

### 4. Index your corpus

```bash
python scripts/index_corpus_to_azure.py --jsonl-path data/irs_tax_knowledge.jsonl
```

This script:
- Loads documents from JSONL
- Generates embeddings using Azure OpenAI
- Uploads documents to the index in batches

### 5. Switch the retriever

Option A: Replace the existing `vector_db.py`:
```bash
mv backend/services/vector_db.py backend/services/vector_db_faiss.py
mv backend/services/vector_db_azure_search.py backend/services/vector_db.py
```

Option B: Keep both and use environment variable to switch:
```python
# backend/services/vector_db.py
USE_AZURE_SEARCH = os.getenv("USE_AZURE_SEARCH", "false").lower() == "true"

if USE_AZURE_SEARCH:
    from .vector_db_azure_search import similarity_search
else:
    from .vector_db_faiss import similarity_search
```

### 6. Test the integration

```bash
# Start the API
uvicorn app.main:app --reload

# In another terminal, test the orchestration endpoint
curl -X POST http://localhost:8000/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "customer": {
      "id": "U1",
      "email": "test@example.com",
      "last_event": "payment_plans",
      "properties": {"form_started": "yes"}
    }
  }'
```

---

## Implementation details

### Files created/modified

1. **`HYBRID_SEARCH_MIGRATION.md`** — Full migration guide with architecture
2. **`backend/services/vector_db_azure_search.py`** — Drop-in replacement for FAISS
3. **`backend/scripts/setup_azure_search_index.py`** — Index creation script
4. **`backend/scripts/index_corpus_to_azure.py`** — Corpus ingestion script

### API compatibility

The Azure Search adapter maintains the same interface as the FAISS version:

```python
# Same function signature
similarity_search(query: str, k: int) -> List[Document]

# Returns LangChain Documents with metadata
document.page_content  # "The text of the document"
document.metadata      # {id, title, section, url, published_date, source, score, rerank_score}
```

The retriever agent needs no changes:
```python
# backend/agents/retriever.py — no modifications needed
from services.vector_db import similarity_search
docs = similarity_search(query_text, k=5)
```

### Hybrid vs. pure vector search

The `similarity_search` function supports two modes:

**Hybrid (default):**
```python
docs = similarity_search(query, k=5, hybrid=True, semantic=False)
```
- Combines BM25 keyword search + vector search
- Better for mixed relevance (keyword + semantic)
- Recommended for general use

**Pure vector search:**
```python
docs = similarity_search(query, k=5, hybrid=False, semantic=False)
```
- Vector embeddings only
- Slower but more semantic matching
- Use when keywords alone don't capture intent

**With semantic re-ranking (Premium tier only):**
```python
docs = similarity_search(query, k=5, hybrid=True, semantic=True)
```
- Applies LLM-based re-ranking to top results
- Increases latency but improves final ranking
- Requires Azure Search Premium SKU

---

## Production checklist

- [ ] Create Azure Search resource (Standard or Premium tier)
- [ ] Set up Azure OpenAI with embeddings deployment
- [ ] Configure `.env` with Azure credentials
- [ ] Run `setup_azure_search_index.py` to create index
- [ ] Run `index_corpus_to_azure.py` to upload documents
- [ ] Update `backend/services/vector_db.py` to use Azure Search
- [ ] Run integration tests with `Orchestrator.run_flow`
- [ ] Monitor Azure Search metrics (queries/sec, latency, errors)
- [ ] Set up backups and disaster recovery
- [ ] Document the Azure Search resource in your runbook

---

## Troubleshooting

**"AZURE_SEARCH_ENDPOINT not set"**
- Ensure `.env` has the correct Azure Search endpoint URL (format: `https://<service>.search.windows.net`)

**"Index creation failed: field 'text_vector' has invalid dimension"**
- Verify the embedding model outputs 1536 dimensions (Azure OpenAI text-embedding-3-small)
- Update `vector_search_dimensions` in the index schema if using a different model

**"Hybrid search not working"**
- Ensure index has both text fields and a vector field named `text_vector`
- Check that the query generates an embedding successfully

**"Semantic search returns no rerank_score"**
- Semantic re-ranking requires Premium SKU
- On Standard tier, `rerank_score` will be None

**Slow indexing**
- Increase batch size in `index_corpus_to_azure.py` (default 100)
- Run multiple indexing jobs in parallel (different document ranges)
- Pre-compute embeddings offline and upload directly

---

## Performance tips

1. **Use hybrid search by default** — better recall than vector-only
2. **Semantic re-ranking judiciously** — add latency, use only for top results
3. **Batch uploads** — index documents in chunks to avoid timeouts
4. **Cache embeddings** — store query embeddings in Redis to avoid recomputation
5. **Index filters** — use source or type filters to reduce search scope
6. **Monitor costs** — Azure Search bills by index size and queries; optimize queries

---

## Cost comparison

| Model | Cost | Pros | Cons |
|-------|------|------|------|
| FAISS (local) | $0 | Free, no Azure costs | Doesn't scale, manual indexing |
| Azure Search Standard | ~$70-200/mo | Managed, hybrid search | Semantic limited |
| Azure Search Premium | ~$400+/mo | Full semantic, high scale | Higher cost |

---

## References

- [Azure AI Search documentation](https://learn.microsoft.com/en-us/azure/search/)
- [Hybrid search implementation](https://learn.microsoft.com/en-us/azure/search/hybrid-search-how-to-query)
- [Semantic search](https://learn.microsoft.com/en-us/azure/search/semantic-search-overview)
- [Python SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/search-documents-readme)

---

## Next steps

1. Deploy to Azure and run end-to-end tests
2. Collect search quality metrics (click-through rate, relevance feedback)
3. Fine-tune semantic configuration based on domain feedback
4. Integrate search analytics into your observability stack
