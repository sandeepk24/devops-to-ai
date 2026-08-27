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

RAG_URL = os.environ.get("RAG_URL", "http://localhost:8081").rstrip("/")

GOLDEN = [
    {
        "question": "How do we roll back a bad model canary?",
        "expect_source_substr": "canary-rollback",
    },
    {
        "question": "What is continuous batching and why does it matter?",
        "expect_source_substr": "continuous-batching",
    },
    {
        "question": "What are the failure modes of RAG?",
        "expect_source_substr": "rag-ops",
    },
]


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
    # Ensure corpus is loaded.
    try:
        ingest = post_json(f"{RAG_URL}/v1/rag/ingest", {})
        print(f"ingest: {ingest}")
    except urllib.error.URLError as exc:
        print(f"FAIL: cannot reach RAG service at {RAG_URL}: {exc}", file=sys.stderr)
        return 2

    failures = 0
    for case in GOLDEN:
        result = post_json(f"{RAG_URL}/v1/rag/query", {"question": case["question"]})
        sources = [s.get("source", "") for s in result.get("sources", [])]
        ok = any(case["expect_source_substr"] in s for s in sources)
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
