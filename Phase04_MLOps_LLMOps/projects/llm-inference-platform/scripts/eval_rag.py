#!/usr/bin/env python3
"""
Tiny offline-ish RAG eval harness for Phase 04.

Calls the running RAG service with a golden question set and checks that
expected source filenames appear in the sources list.

Usage:
    python scripts/eval_rag.py
    RAG_URL=http://localhost:8081 python scripts/eval_rag.py
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

RAG_URL = os.environ.get("RAG_URL", "http://localhost:8081").rstrip("/")
GOLDEN_PATH = Path(
    os.environ.get(
        "GOLDEN_SET",
        str(Path(__file__).resolve().parents[1] / "data" / "eval" / "golden_set.jsonl"),
    )
)


def load_golden(path: Path) -> list[dict]:
    cases: list[dict] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            cases.append(json.loads(line))
    return cases


def post_json(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    if not GOLDEN_PATH.exists():
        print(f"FAIL: golden set not found at {GOLDEN_PATH}", file=sys.stderr)
        return 2

    # Ensure corpus is loaded.
    try:
        ingest = post_json(f"{RAG_URL}/v1/rag/ingest", {})
        print(f"ingest: {ingest}")
    except urllib.error.URLError as exc:
        print(f"FAIL: cannot reach RAG service at {RAG_URL}: {exc}", file=sys.stderr)
        return 2

    failures = 0
    for case in load_golden(GOLDEN_PATH):
        result = post_json(f"{RAG_URL}/v1/rag/query", {"question": case["question"]})
        sources = [s.get("source", "") for s in result.get("sources", [])]
        needle = case["expect_source_substr"]
        ok = any(needle in s for s in sources)
        status = "PASS" if ok else "FAIL"
        print(f"{status}: {case['question']}")
        print(f"  sources={sources}")
        print(f"  answer_preview={str(result.get('answer', ''))[:120]!r}")
        if not ok:
            failures += 1

    if failures:
        print(f"\n{failures} failing case(s)")
        return 1
    print("\nAll golden cases passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
