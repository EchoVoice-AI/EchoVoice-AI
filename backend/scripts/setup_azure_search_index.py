# backend/scripts/setup_azure_search_index.py

"""
Setup script to create an Azure Search index with fields for hybrid semantic search.

Run with:
    cd backend
    python scripts/setup_azure_search_index.py

Requires:
  - AZURE_SEARCH_ENDPOINT
  - AZURE_SEARCH_KEY
  - AZURE_SEARCH_INDEX (optional, defaults to 'echvoice-index')
  - AZURE_OPENAI_* variables
"""

import os
import sys
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
)
from azure.identity import AzureKeyCredential


def create_search_index():
    """Create an Azure Search index for hybrid semantic search."""
    
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    key = os.getenv("AZURE_SEARCH_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX", "echvoice-index")

    if not endpoint or not key:
        print(
            "ERROR: AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY "
            "environment variables must be set."
        )
        sys.exit(1)

    print(f"Creating search index '{index_name}' at {endpoint}...")

    # Initialize index client
    index_client = SearchIndexClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )

    # Define index fields
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="title", type=SearchFieldDataType.String),
        SearchableField(name="section", type=SearchFieldDataType.String),
        SearchableField(
            name="text",
            type=SearchFieldDataType.String,
            analyzer_name="en.microsoft",  # Microsoft English analyzer
        ),
        SimpleField(name="url", type=SearchFieldDataType.String),
        SimpleField(name="published_date", type=SearchFieldDataType.String),
        SimpleField(name="source", type=SearchFieldDataType.String),
        # Vector field for semantic search
        SearchField(
            name="text_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,  # Azure OpenAI text-embedding-3-small dimension
            vector_search_profile_name="myHnsw",
        ),
    ]

    # Configure vector search with HNSW algorithm
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(name="myHnsw"),
        ],
        profiles=[
            VectorSearchProfile(
                name="myHnsw",
                algorithm_configuration_name="myHnsw",
            ),
        ],
    )

    # Configure semantic search (requires Premium tier)
    semantic_search = SemanticSearch(
        configurations=[
            SemanticConfiguration(
                name="default",
                prioritized_fields=SemanticPrioritizedFields(
                    title_field=SemanticField(field_name="title"),
                    content_fields=[SemanticField(field_name="text")],
                ),
            ),
        ]
    )

    # Create index
    index = SearchIndex(
        name=index_name,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search,
    )

    try:
        result = index_client.create_index(index)
        print(f"✓ Index '{result.name}' created successfully!")
        print(f"  Vector search: HNSW (dim={result.fields[-1].vector_search_dimensions})")
        print("  Semantic search: enabled for 'title' and 'text' fields")
        return True
    except Exception as e:
        print(f"✗ Failed to create index: {e}")
        return False


if __name__ == "__main__":
    success = create_search_index()
    sys.exit(0 if success else 1)
