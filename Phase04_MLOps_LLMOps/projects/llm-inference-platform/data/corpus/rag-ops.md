# RAG operations guide

Retrieval-Augmented Generation (RAG) grounds LLM answers in your documents.

## Pipeline

1. Chunk documents with overlap
2. Embed chunks into vectors
3. Store vectors + metadata in a vector database (Qdrant here)
4. Embed the user question and retrieve top-k similar chunks
5. Build a prompt with retrieved context and ask the LLM
6. Return the answer with citations

## Failure modes

- Bad chunking → irrelevant retrieval
- Stale corpus → confident wrong answers after docs change
- Untrusted documents → prompt injection via retrieved text
- Empty retrieval → must decline instead of hallucinating

## Re-ingest

After updating files under `data/corpus/`, call `POST /v1/rag/ingest` on the RAG service.
