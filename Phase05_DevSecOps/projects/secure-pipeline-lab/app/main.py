"""
Phase 05 secure-pipeline-lab — tiny API to scan and ship.

Keep it small on purpose. The learning is the gates around the image,
not a large feature set.
"""

from fastapi import FastAPI

app = FastAPI(title="secure-pipeline-lab", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/info")
def info() -> dict[str, str]:
    return {
        "service": "secure-pipeline-lab",
        "phase": "05",
        "hint": "Scan me, don't just curl me.",
    }
