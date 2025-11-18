# Retriever Agent

Purpose

- Fetch approved content and citations relevant to a customer's context (e.g., product docs). Used for RAG-style generation.

Location

- `backend/agents/retriever.py`

API / Contract

- Function: `retrieve_citations(customer: dict) -> list`
- Input: `customer` object. Retriever may inspect `customer['properties']` (e.g., `product_id`).
- Output: List of citation objects: `{ 'id': str, 'title': str, 'content': str, 'source': str }`.

Example

```py
from agents.retriever import retrieve_citations

cust = { 'properties': { 'product_id': 'p_101' } }
citations = retrieve_citations(cust)
# citations -> [ { 'id': 'p_101', 'content': '...', 'source': 'product_docs' } ]
```

Notes

- The scaffold uses `backend/services/vector_db.py` simple lookup. Replace with vector search (Pinecone/Azure) for production.
