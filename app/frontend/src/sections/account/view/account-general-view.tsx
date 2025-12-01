'use client';

import { RetrieverGeneral } from '../account-general';

// ----------------------------------------------------------------------

export function AccountGeneralView({ retriever }: { retriever?: any }) {
  const retriever2 = {
    queryRewrite: true,
    useOidFilter: false,
    useGroupFilter: true,
    name: "Default Retriever",
    description: "This is the default retriever..",
    createdAt: "2023-10-01T12:00:00Z",
    updatedAt: "2023-10-15T15:30:00Z",
    retrieverType: "hybrid",
    retrievalMode: "hybrid",
    indexer: "default-indexer",
    textEmbeddings: true,
    embeddings: true,
    imageEmbeddings: false,
    allowOidFilter: false,
    allowGroupFilter: true,
    ...retriever,
  }
  return <RetrieverGeneral retriever={retriever2} />;
}
