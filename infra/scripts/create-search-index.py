#!/usr/bin/env python3
"""
Simple helper to create a Cognitive Search index. Update `SEARCH_ENDPOINT`
and `ADMIN_KEY` environment variables before running. This is a convenience
script for local development and is not a replacement for production IaC.
"""
import os
import sys
import json
from azure.core.exceptions import ResourceExistsError
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex, SimpleField, SearchableField, edm

SEARCH_ENDPOINT = os.environ.get('SEARCH_ENDPOINT')
ADMIN_KEY = os.environ.get('SEARCH_ADMIN_KEY')

if not SEARCH_ENDPOINT or not ADMIN_KEY:
    print('Set SEARCH_ENDPOINT and SEARCH_ADMIN_KEY env vars')
    sys.exit(2)

client = SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=ADMIN_KEY)

index_name = 'documents'

fields = [
    SimpleField(name='id', type=edm.String, key=True),
    SearchableField(name='content', type=edm.String, analyzer_name='en.lucene'),
    SimpleField(name='source', type=edm.String, filterable=True, sortable=False),
]

index = SearchIndex(name=index_name, fields=fields)

try:
    client.create_index(index)
    print(f'Index "{index_name}" created')
except ResourceExistsError:
    print(f'Index "{index_name}" already exists')

print('Done')
