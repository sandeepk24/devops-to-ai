"""
rag-service — Phase 04 capstone.

Ingest ops docs into Qdrant, retrieve top-k chunks, and generate a
grounded answer via the inference gateway.

Default embeddings are a lightweight hashing encoder so the image stays
small and CPU-friendly. Swap in sentence-transformers when you're ready
(see TODO below).

Usage:
    pip install -r requirements.txt
    uvicorn main:app --host 0.0.0.0 --port 8081
"""

import hashlib
import os
import re
from pathlib import Path
from typing import Any, Optional

import httpx
import structlog
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
from qdrant_client.http import models as qm

# ── configuration ──────────────────────────────────────────────────────────────
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://inference-gateway:8080").rstrip("/")
GATEWAY_API_KEY = os.getenv("GATEWAY_API_KEY", "dev-key")
# If API_KEYS is a comma list, use the first key for outbound calls.
if "," in GATEWAY_API_KEY:
    GATEWAY_API_KEY = GATEWAY_API_KEY.split(",", 1)[0].strip()

CORPUS_DIR = Path(os.getenv("CORPUS_DIR", "/data/corpus"))
PROMPTS_DIR = Path(os.getenv("PROMPTS_DIR", "/prompts"))
COLLECTION = os.getenv("QDRANT_COLLECTION", "ops_docs")
TOP_K = int(os.getenv("TOP_K", "4"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "80"))
EMBED_DIM = 64
PORT = int(os.getenv("PORT", "8081"))

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
)
log = structlog.get_logger()

app = FastAPI(title="rag-service", version="0.1.0")
qdrant = QdrantClient(url=QDRANT_URL)


class RagQuery(BaseModel):
    question: str = Field(min_length=3)
    top_k: Optional[int] = None


def hash_embed(text: str, dim: int = EMBED_DIM) -> list[float]:
    """
    Tiny deterministic bag-of-tokens embedding for local demos.

    TODO: replace with sentence-transformers (e.g. all-MiniLM-L6-v2) or an
    embedding API. Keep the function signature identical so Qdrant code
    does not need to change.
    """
    vec = [0.0] * dim
    tokens = re.findall(r"[a-z0-9_]+", text.lower())
    if not tokens:
        return vec
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:4], "big") % dim
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vec[idx] += sign
    # L2 normalise
    norm = sum(v * v for v in vec) ** 0.5 or 1.0
    return [v / norm for v in vec]


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + size)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks


def load_system_prompt() -> str:
    path = PROMPTS_DIR / "rag_system_v1.txt"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return (
        "You are an ops assistant. Answer using ONLY the provided context. "
        "If the context is insufficient, say you do not have enough information. "
        "Cite sources by filename."
    )


def ensure_collection() -> None:
    names = {c.name for c in qdrant.get_collections().collections}
    if COLLECTION in names:
        return
    qdrant.create_collection(
        collection_name=COLLECTION,
        vectors_config=qm.VectorParams(size=EMBED_DIM, distance=qm.Distance.COSINE),
    )
    log.info("collection_created", collection=COLLECTION)


@app.on_event("startup")
def startup() -> None:
    ensure_collection()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/rag/ingest")
def ingest_corpus() -> dict[str, Any]:
    """Read markdown/text files from CORPUS_DIR and upsert into Qdrant."""
    ensure_collection()
    if not CORPUS_DIR.exists():
        raise HTTPException(status_code=500, detail=f"Corpus dir missing: {CORPUS_DIR}")

    points: list[qm.PointStruct] = []
    files_seen = 0
    for path in sorted(CORPUS_DIR.rglob("*")):
        if path.suffix.lower() not in {".md", ".txt"}:
            continue
        files_seen += 1
        content = path.read_text(encoding="utf-8")
        for i, chunk in enumerate(chunk_text(content)):
            point_id = int(hashlib.md5(f"{path}:{i}".encode()).hexdigest()[:16], 16)
            points.append(
                qm.PointStruct(
                    id=point_id,
                    vector=hash_embed(chunk),
                    payload={
                        "text": chunk,
                        "source": str(path.relative_to(CORPUS_DIR)),
                        "chunk_index": i,
                    },
                )
            )

    if points:
        qdrant.upsert(collection_name=COLLECTION, points=points)

    log.info("ingest_complete", files=files_seen, chunks=len(points))
    return {"files": files_seen, "chunks": len(points), "collection": COLLECTION}


@app.post("/v1/rag/query")
async def rag_query(body: RagQuery) -> dict[str, Any]:
    ensure_collection()
    k = body.top_k or TOP_K
    query_vec = hash_embed(body.question)

    hits = qdrant.search(collection_name=COLLECTION, query_vector=query_vec, limit=k)
    sources = [
        {
            "source": h.payload.get("source"),
            "score": h.score,
            "text": h.payload.get("text"),
        }
        for h in hits
        if h.payload
    ]

    if not sources:
        return {
            "answer": "I don't have enough context in the knowledge base to answer that.",
            "sources": [],
            "model": None,
        }

    context_blocks = []
    for i, src in enumerate(sources, start=1):
        context_blocks.append(f"[{i}] ({src['source']})\n{src['text']}")
    context = "\n\n".join(context_blocks)

    system_prompt = load_system_prompt()
    user_prompt = (
        f"Context:\n{context}\n\n"
        f"Question: {body.question}\n\n"
        "Answer with citations like [1], [2] referring to the context blocks."
    )

    payload = {
        "model": "mock-model",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": 256,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{GATEWAY_URL}/v1/chat/completions",
                json=payload,
                headers={
                    "Authorization": f"Bearer {GATEWAY_API_KEY}",
                    "Content-Type": "application/json",
                },
            )
        resp.raise_for_status()
        data = resp.json()
        answer = data["choices"][0]["message"]["content"]
        model = data.get("model")
    except Exception as exc:
        log.error("generation_failed", error=str(exc))
        raise HTTPException(status_code=502, detail=f"Generation via gateway failed: {exc}") from exc

    return {
        "answer": answer,
        "sources": [{"source": s["source"], "score": s["score"]} for s in sources],
        "model": model,
    }
