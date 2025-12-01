"""Vector Search Retriever (Phase 2)

Simulates a vector DB lookup using `context_query` and returns `retrieved_content`.
In production this node would call a client for Pinecone/Chroma/Azure Search.
"""
from typing import Dict, Any, List
from PersonalizeAI.state import GraphState


def vector_search_retriever(state: GraphState) -> Dict[str, Any]:
    """Execute the vector search and return retrieved documents.

    This is a deterministic simulation based on the query string.
    """
    query = (state.get("context_query") or "").lower()

    # --- Simulated vector search results ---
    if "nutritional details" in query or "nutritional" in query:
        content = [
            {"text": "Our new protein bar contains 20g of high-quality whey protein and zero added sugar.", "source_id": "product-db#456"},
            {"text": "Whey protein is an approved, citable ingredient per brand guideline v2.1.", "source_id": "brand-guidelines#001"},
        ]
    else:
        content = [
            {"text": "Company history: Founded in 2010 to empower healthy living.", "source_id": "about-us#01"},
            {"text": "General sales policy: All sales are final after 30 days.", "source_id": "legal-doc#999"},
        ]

    print(f"Retrieved {len(content)} documents for query: '{query}'")

    return {"retrieved_content": content}
