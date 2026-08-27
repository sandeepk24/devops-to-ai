"""
mock-inference — CPU-friendly OpenAI-compatible stub for Phase 04.

Implements a minimal /v1/chat/completions so the gateway and RAG service
can be developed without a GPU. Responses are deterministic templates,
not a real model.

Usage:
    uvicorn main:app --host 0.0.0.0 --port 8000
"""

import time
import uuid
from typing import Any, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="mock-inference", version="0.1.0")
MODEL_NAME = "mock-model"


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = MODEL_NAME
    messages: list[ChatMessage]
    max_tokens: int = Field(default=128, ge=1, le=2048)
    temperature: float = 0.0
    stream: bool = False


def _last_user_text(messages: list[ChatMessage]) -> str:
    for message in reversed(messages):
        if message.role == "user":
            return message.content
    return ""


def _fake_completion(user_text: str, max_tokens: int) -> str:
    snippet = user_text.strip().replace("\n", " ")[:180] or "(empty prompt)"
    body = (
        "This is a mock inference response for local Phase 04 development. "
        f"You asked: '{snippet}'. "
        "Replace this service with vLLM when you have a GPU. "
        "Key platform metrics to watch: TTFT, tokens/sec, error rate, queue depth."
    )
    # Rough token stand-in: ~4 chars per token
    return body[: max_tokens * 4]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    return {"status": "ready"}


@app.get("/v1/models")
def list_models() -> dict[str, Any]:
    return {
        "object": "list",
        "data": [{"id": MODEL_NAME, "object": "model", "owned_by": "phase04-mock"}],
    }


@app.post("/v1/chat/completions")
def chat_completions(req: ChatCompletionRequest) -> dict[str, Any]:
    # Streaming is intentionally unsupported in the mock — keep clients simple.
    if req.stream:
        return {
            "error": {
                "message": "stream=true is not supported by mock-inference",
                "type": "invalid_request_error",
            }
        }

    started = time.time()
    content = _fake_completion(_last_user_text(req.messages), req.max_tokens)
    # Simulate a little prefill latency so dashboards are not all zeros.
    time.sleep(0.05)

    prompt_tokens = max(1, sum(len(m.content) for m in req.messages) // 4)
    completion_tokens = max(1, len(content) // 4)

    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:24]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": req.model or MODEL_NAME,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
        "mock_meta": {
            "latency_ms": int((time.time() - started) * 1000),
            "note": "Not a real model — swap INFERENCE_URL to vLLM for production practice",
        },
    }
