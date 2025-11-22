# backend/scripts/index_corpus_to_azure.py

"""
Upload corpus from JSONL file to Azure Search index with embeddings.

Run with:
    cd backend
    python scripts/index_corpus_to_azure.py [--jsonl-path data/irs_tax_knowledge.jsonl]

Requires:
  - AZURE_SEARCH_ENDPOINT
  - AZURE_SEARCH_KEY
  - AZURE_SEARCH_INDEX (optional, defaults to 'echvoice-index')
  - AZURE_OPENAI_* variables for embeddings
"""

import json
import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any

from azure.search.documents import SearchClient
from azure.search.documents.models import IndexDocumentsBatch
from azure.identity import AzureKeyCredential
from langchain_openai import AzureOpenAIEmbeddings


def load_jsonl(jsonl_path: str) -> List[Dict[str, Any]]:
    """Load documents from JSONL file."""
    documents = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                doc = json.loads(line)
                documents.append(doc)
            except json.JSONDecodeError as e:
                print(f"Warning: skipping malformed JSON line: {e}")
    return documents


def index_corpus(
    jsonl_path: str,
    batch_size: int = 100,
    skip_vectorization: bool = False,
):
    """
    Load JSONL corpus and upload to Azure Search with embeddings.
    
    Args:
        jsonl_path: Path to JSONL file.
        batch_size: Number of documents per batch upload.
        skip_vectorization: If True, skip embedding generation (assumes 'text_vector' field exists).
    """
    
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    key = os.getenv("AZURE_SEARCH_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX", "echvoice-index")

    if not endpoint or not key:
        print(
            "ERROR: AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY "
            "environment variables must be set."
        )
        sys.exit(1)

    print(f"Loading corpus from {jsonl_path}...")
    documents = load_jsonl(jsonl_path)
    print(f"Loaded {len(documents)} documents.")

    # Initialize Azure Search client
    search_client = SearchClient(
        endpoint=endpoint,
        index_name=index_name,
        credential=AzureKeyCredential(key),
    )

    # Initialize embeddings if needed
    if not skip_vectorization:
        print("Initializing Azure OpenAI embeddings...")
        embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT"),
        )

    # Process and upload in batches
    print(f"Uploading documents in batches of {batch_size}...")
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i : i + batch_size]
        
        # Generate embeddings if needed
        if not skip_vectorization:
            print(f"  Generating embeddings for batch {i // batch_size + 1}...")
            for doc in batch_docs:
                text = doc.get("text", "")
                if text:
                    doc["text_vector"] = embeddings.embed_query(text)
        
        # Upload batch
        batch = IndexDocumentsBatch()
        batch.add_upload_actions(batch_docs)
        
        try:
            result = search_client.index_documents(batch)
            uploaded = sum(1 for r in result if r.succeeded)
            print(f"  ✓ Batch {i // batch_size + 1}: {uploaded}/{len(batch_docs)} uploaded")
        except Exception as e:
            print(f"  ✗ Batch upload failed: {e}")
            sys.exit(1)

    print(f"✓ Successfully indexed {len(documents)} documents to '{index_name}'")


def main():
    parser = argparse.ArgumentParser(
        description="Upload JSONL corpus to Azure Search with embeddings."
    )
    parser.add_argument(
        "--jsonl-path",
        type=str,
        default="data/irs_tax_knowledge.jsonl",
        help="Path to JSONL corpus file.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of documents per batch.",
    )
    parser.add_argument(
        "--skip-vectorization",
        action="store_true",
        help="Skip embedding generation (assumes 'text_vector' field exists).",
    )

    args = parser.parse_args()

    if not os.path.exists(args.jsonl_path):
        print(f"ERROR: JSONL file not found: {args.jsonl_path}")
        sys.exit(1)

    index_corpus(
        jsonl_path=args.jsonl_path,
        batch_size=args.batch_size,
        skip_vectorization=args.skip_vectorization,
    )


if __name__ == "__main__":
    main()
