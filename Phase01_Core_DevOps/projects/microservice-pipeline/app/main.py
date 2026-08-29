"""
Phase 01 capstone — small FastAPI service.

Endpoints you'll need for health checks and a tiny CRUD-ish demo.
Fill TODOs as you grow the app (persistence, validation, etc.).
"""

from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="phase01-api", version="0.1.0")

# In-memory store for the starter. Swap for Postgres when you're ready.
_ITEMS: dict[int, dict] = {
    1: {"id": 1, "name": "deploy checklist", "done": False},
    2: {"id": 2, "name": "write Dockerfile", "done": True},
}
_NEXT_ID = 3


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    done: bool = False


class Item(ItemCreate):
    id: int


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness — process is up."""
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    """
    Readiness — safe to receive traffic.

    TODO: if you wire Postgres, check DB connectivity here and return 503 on failure.
    """
    return {"status": "ready"}


@app.get("/v1/items", response_model=list[Item])
def list_items() -> list[dict]:
    return list(_ITEMS.values())


@app.get("/v1/items/{item_id}", response_model=Item)
def get_item(item_id: int) -> dict:
    item = _ITEMS.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="item not found")
    return item


@app.post("/v1/items", response_model=Item, status_code=201)
def create_item(body: ItemCreate) -> dict:
    global _NEXT_ID
    item = {"id": _NEXT_ID, "name": body.name, "done": body.done}
    _ITEMS[_NEXT_ID] = item
    _NEXT_ID += 1
    return item
