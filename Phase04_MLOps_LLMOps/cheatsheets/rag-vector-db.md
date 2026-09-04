# RAG & vector database cheatsheet

**Use this when:** the model shouldn't invent answers from private runbooks — you retrieve chunks, then generate with citations.  
**Rule of thumb:** empty retrieval → say you don't know. Never "helpfully" guess kubectl.

Phase 04 Path A uses a tiny hash embedder so Docker stays light. Treat that as scaffolding; the pipeline shape is the same when you swap in real embeddings.

---

## Pipeline

```
docs → chunk → embed → upsert vectors
query → embed → search top-k → prompt(context) → LLM → answer + citations
```

---

## Chunking starting points

| Strategy | Use when |
|---|---|
| Fixed size + overlap | Simple ops docs / READMEs |
| Split on headings | Well-structured markdown |
| Semantic chunking | Noisy long PDFs (more moving parts) |

Start: chunk 400–800 characters, overlap ~10–20%. Measure retrieval hit-rate; then tune.

---

## Qdrant quickstart

```bash
docker run -p 6333:6333 qdrant/qdrant:v1.13.2
```

Create collection (cosine, 384-dim example for MiniLM):

```python
from qdrant_client import QdrantClient
from qdrant_client.http import models as qm

client = QdrantClient(url="http://localhost:6333")
client.create_collection(
    collection_name="ops_docs",
    vectors_config=qm.VectorParams(size=384, distance=qm.Distance.COSINE),
)
```

Search:

```python
hits = client.search(collection_name="ops_docs", query_vector=vec, limit=4)
```

Always store `source`, `chunk_index`, and raw `text` in the payload.

---

## Metadata filters

```python
query_filter=qm.Filter(
    must=[qm.FieldCondition(key="env", match=qm.MatchValue(value="prod"))]
)
```

Use filters to avoid retrieving staging runbooks in production answers.

---

## Prompt shape

```
[system]  Answer only from context. Cite [n]. Decline if insufficient.
[user]    Context:
          [1] (file.md) ...
          [2] (other.md) ...

          Question: ...
```

---

## Evaluation (minimum viable)

Keep a `golden_set.jsonl`:

```json
{"question": "How do we roll back a canary?", "expect_source": "canary-rollback.md"}
```

Pass criteria:
- Expected source appears in top-k
- Answer does not invent steps absent from context
- Empty corpus → explicit decline

---

## Failure modes → fixes

| Symptom | Likely cause | Fix |
|---|---|---|
| Irrelevant citations | Chunks too big/small | Retune chunking |
| Misses obvious doc | Weak embeddings / no hybrid search | Better model or BM25 hybrid |
| Confident nonsense | Empty retrieval ignored | Hard-fail when k=0 |
| Prompt injection | Untrusted corpus | Sanitize, cite, strip instructions in docs |
| Stale answers | No re-ingest | Automate ingest on doc change |

---

## When not to use RAG

- Knowledge fits in the system prompt permanently
- You need to change model behaviour/style globally → prompt or fine-tune
- Latency budget cannot afford retrieval + generation
