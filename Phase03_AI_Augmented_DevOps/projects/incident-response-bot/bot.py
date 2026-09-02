"""
AI-powered incident response bot — Phase 03 capstone.

Path A (default): MOCK_MODE=true — fake logs/metrics, print diagnosis to the terminal.
Path B: point PROMETHEUS_URL / LOKI_URL at your Phase 02 stack and set MOCK_MODE=false.
Path C: set SLACK_BOT_TOKEN to post into a channel.

Usage:
    pip install -r requirements.txt
    cp .env.example .env   # add ANTHROPIC_API_KEY at minimum
    python bot.py

    curl -X POST http://localhost:8000/webhook -H 'Content-Type: application/json' -d @sample-alert.json
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import httpx
import structlog
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

load_dotenv()

# ── configuration ──────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "anthropic").lower()  # anthropic | openai | mock-llm
MOCK_MODE = os.environ.get("MOCK_MODE", "true").lower() in ("1", "true", "yes")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_INCIDENT_CHANNEL = os.environ.get("SLACK_INCIDENT_CHANNEL", "#incidents")
PROMETHEUS_URL = os.environ.get("PROMETHEUS_URL", "http://localhost:9090").rstrip("/")
LOKI_URL = os.environ.get("LOKI_URL", "http://localhost:3100").rstrip("/")
PORT = int(os.environ.get("PORT", "8000"))

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

app = FastAPI(title="incident-response-bot", version="0.1.0")
PROMPTS_DIR = Path(__file__).parent / "prompts"


# ── context gathering ──────────────────────────────────────────────────────────

async def get_loki_logs(service: str, minutes: int = 30) -> str:
    """Fetch recent error logs. Never raises — returns a string always."""
    if MOCK_MODE:
        return (
            f'{{"level":"error","service":"{service}","msg":"upstream timeout after 30s"}}\n'
            f'{{"level":"error","service":"{service}","msg":"connection reset by peer"}}\n'
            f'{{"level":"warn","service":"{service}","msg":"retrying payment processor"}}\n'
            "(MOCK_MODE — replace with real Loki queries)"
        )

    # TODO Path B: query Loki range API and return last ~50 error lines
    # GET {LOKI_URL}/loki/api/v1/query_range?query=...&start=...&end=...
    try:
        end = datetime.now(timezone.utc)
        start = end - timedelta(minutes=minutes)
        query = f'{{compose_service="{service}"}} |= "error"'
        params = {
            "query": query,
            "start": str(int(start.timestamp() * 1e9)),
            "end": str(int(end.timestamp() * 1e9)),
            "limit": 50,
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{LOKI_URL}/loki/api/v1/query_range", params=params)
            resp.raise_for_status()
            data = resp.json()
        lines: list[str] = []
        for stream in data.get("data", {}).get("result", []):
            for _, line in stream.get("values", []):
                lines.append(line)
        return "\n".join(lines[-50:]) if lines else "No error logs found in window"
    except Exception as exc:
        log.warning("loki_unavailable", error=str(exc))
        return "Loki unavailable — logs not included"


async def get_prometheus_metrics(service: str) -> dict[str, Any]:
    """Fetch golden signals. Never raises."""
    if MOCK_MODE:
        return {
            "error_rate": 4.2,
            "p99_latency": 842.0,
            "rps": 127.0,
            "cpu_percent": None,
            "memory_percent": None,
            "source": "mock",
        }

    # TODO Path B: run real PromQL against PROMETHEUS_URL
    async def _query(promql: str) -> Optional[float]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{PROMETHEUS_URL}/api/v1/query",
                    params={"query": promql},
                )
                resp.raise_for_status()
                result = resp.json().get("data", {}).get("result", [])
                if not result:
                    return None
                return round(float(result[0]["value"][1]), 2)
        except Exception as exc:
            log.warning("prom_query_failed", error=str(exc), query=promql[:80])
            return None

    error_rate = await _query(
        f'sum(rate(http_requests_total{{job="{service}",status=~"5.."}}[5m]))'
        f' / clamp_min(sum(rate(http_requests_total{{job="{service}"}}[5m])), 1e-9) * 100'
    )
    p99 = await _query(
        f'histogram_quantile(0.99, sum by (le) '
        f'(rate(http_request_duration_seconds_bucket{{job="{service}"}}[5m]))) * 1000'
    )
    rps = await _query(f'sum(rate(http_requests_total{{job="{service}"}}[5m]))')
    return {
        "error_rate": error_rate,
        "p99_latency": p99,
        "rps": rps,
        "cpu_percent": None,
        "memory_percent": None,
        "source": "prometheus",
    }


async def get_recent_deployments(service: str, limit: int = 5) -> str:
    """Deploy history. Mock or git log fallback."""
    if MOCK_MODE:
        return (
            "2026-09-01 18:02 UTC | v1.4.2 | deployed by ci-bot\n"
            "2026-08-28 11:15 UTC | v1.4.1 | deployed by ci-bot\n"
            "(MOCK_MODE — wire ArgoCD or git log for Path B)"
        )
    # TODO: ArgoCD history API, or:
    try:
        import subprocess

        result = subprocess.run(
            ["git", "log", "--oneline", f"-{limit}", "--format=%ci %s"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() or "No recent deployments found"
    except Exception:
        return "No recent deployments found"


async def get_pod_events(service: str) -> str:
    if MOCK_MODE:
        return (
            "18:04:01 | Warning | BackOff | Back-off restarting failed container\n"
            "18:03:44 | Warning | Unhealthy | Readiness probe failed\n"
            "(MOCK_MODE — use kubernetes client for Path B)"
        )
    # TODO Path B: kubernetes CoreV1Api list events for the service
    return "Kubernetes events unavailable"


# ── prompts + LLM ──────────────────────────────────────────────────────────────

def load_prompt(name: str) -> str:
    path = PROMPTS_DIR / f"{name}.txt"
    return path.read_text(encoding="utf-8")


def _fill_incident_prompt(
    template: str,
    alert_name: str,
    service: str,
    severity: str,
    logs: str,
    metrics: dict,
    deployments: str,
    pod_events: str,
    fired_at: str,
) -> str:
    # Strip leading comment lines starting with #
    body = "\n".join(
        line for line in template.splitlines() if not line.strip().startswith("#")
    ).strip()
    replacements = {
        "alert_name": alert_name,
        "severity": severity,
        "service": service,
        "fired_at": fired_at,
        "logs": logs,
        "error_rate": str(metrics.get("error_rate")),
        "p99_latency": str(metrics.get("p99_latency")),
        "rps": str(metrics.get("rps")),
        "cpu": str(metrics.get("cpu_percent")),
        "memory": str(metrics.get("memory_percent")),
        "deployments": deployments,
        "pod_events": pod_events,
    }
    for key, value in replacements.items():
        body = body.replace("{" + key + "}", value)
    return body


def _parse_json_loose(text: str) -> dict:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


def _fallback_analysis(reason: str) -> dict:
    return {
        "summary": "AI analysis unavailable — see raw context in logs.",
        "likely_cause": "unknown",
        "confidence": "low",
        "top_checks": [
            "Check recent deployments",
            "Inspect error logs for the service",
            "Verify downstream dependencies",
        ],
        "immediate_actions": ["Page on-call if user impact is ongoing"],
        "related_runbook": None,
        "needs_escalation": True,
        "escalation_reason": reason,
    }


async def analyse_incident(
    alert_name: str,
    service: str,
    severity: str,
    logs: str,
    metrics: dict,
    deployments: str,
    pod_events: str,
    fired_at: str,
) -> dict:
    """Call LLM (or mock-llm) and return structured diagnosis. Never raises."""
    try:
        template = load_prompt("incident-analysis")
        prompt = _fill_incident_prompt(
            template, alert_name, service, severity, logs, metrics, deployments, pod_events, fired_at
        )
    except Exception as exc:
        log.error("prompt_load_failed", error=str(exc))
        return _fallback_analysis(f"prompt load failed: {exc}")

    if LLM_PROVIDER == "mock-llm" or (not ANTHROPIC_API_KEY and not OPENAI_API_KEY):
        log.info("using_mock_llm")
        return {
            "summary": (
                f"{service} shows elevated errors ({metrics.get('error_rate')}%) and "
                f"p99 latency {metrics.get('p99_latency')}ms. Mock LLM suggests upstream timeouts."
            ),
            "likely_cause": "Upstream dependency timeouts (mock diagnosis — set API key for real analysis)",
            "confidence": "medium",
            "top_checks": [
                f"curl the upstream dependency health for {service}",
                "Review error logs for timeout patterns",
                "Check whether a deploy landed in the last 30 minutes",
            ],
            "immediate_actions": [
                "Confirm user impact scope",
                "If deploy-related, prepare rollback plan (do not auto-run)",
            ],
            "related_runbook": "high-error-rate",
            "needs_escalation": False,
            "escalation_reason": None,
        }

    try:
        if LLM_PROVIDER == "openai" or (OPENAI_API_KEY and not ANTHROPIC_API_KEY):
            # Minimal OpenAI Chat Completions call via httpx (no extra SDK required)
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                    json={
                        "model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2,
                    },
                )
                resp.raise_for_status()
                text = resp.json()["choices"][0]["message"]["content"]
        else:
            from anthropic import Anthropic

            client = Anthropic(api_key=ANTHROPIC_API_KEY)
            response = client.messages.create(
                model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5"),
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text

        log.info("llm_raw_response", preview=text[:200])
        return _parse_json_loose(text)
    except Exception as exc:
        log.error("llm_failed", error=str(exc))
        return _fallback_analysis(str(exc))


# ── output formatting ──────────────────────────────────────────────────────────

def format_slack_message(
    alert_name: str,
    service: str,
    severity: str,
    analysis: dict,
    metrics: dict,
    fired_at: str,
) -> list:
    """Slack Block Kit blocks (also useful as structured console output)."""
    icon = {"critical": "🚨", "warning": "⚠️"}.get(severity.lower(), "ℹ️")
    checks = analysis.get("top_checks") or []
    actions = analysis.get("immediate_actions") or []
    checks_md = "\n".join(f"{i}. {c}" for i, c in enumerate(checks, 1)) or "_none_"
    actions_md = "\n".join(f"→ {a}" for a in actions) or "_none_"

    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{icon} {severity.upper()}: {alert_name} — {service}",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*Error rate:* {metrics.get('error_rate')}%  |  "
                    f"*p99:* {metrics.get('p99_latency')}ms  |  "
                    f"*RPS:* {metrics.get('rps')}"
                ),
            },
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Summary*\n{analysis.get('summary', '')}"},
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Likely cause* ({analysis.get('confidence', '?')})\n{analysis.get('likely_cause', '')}",
            },
        },
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*Top checks*\n{checks_md}"}},
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*Immediate actions*\n{actions_md}"}},
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Fired at: {fired_at} | mock={MOCK_MODE} | provider={LLM_PROVIDER}",
                }
            ],
        },
    ]


def print_console_report(
    alert_name: str,
    service: str,
    severity: str,
    analysis: dict,
    metrics: dict,
    fired_at: str,
) -> None:
    """Path A: always print a readable report so you don't need Slack."""
    print("\n" + "=" * 60)
    print(f"INCIDENT: {severity.upper()} {alert_name} — {service}")
    print(f"Fired at: {fired_at}")
    print("-" * 60)
    print(
        f"Metrics: error_rate={metrics.get('error_rate')}%  "
        f"p99={metrics.get('p99_latency')}ms  rps={metrics.get('rps')}"
    )
    print(f"\nSummary:\n  {analysis.get('summary')}")
    print(f"\nLikely cause ({analysis.get('confidence')}):\n  {analysis.get('likely_cause')}")
    print("\nTop checks:")
    for i, check in enumerate(analysis.get("top_checks") or [], 1):
        print(f"  {i}. {check}")
    print("\nImmediate actions:")
    for action in analysis.get("immediate_actions") or []:
        print(f"  → {action}")
    print("=" * 60 + "\n")


async def post_to_slack(
    channel: str,
    alert_name: str,
    service: str,
    severity: str,
    analysis: dict,
    metrics: dict,
    fired_at: str,
) -> bool:
    if not SLACK_BOT_TOKEN:
        log.info("slack_skipped", reason="SLACK_BOT_TOKEN not set")
        return False
    try:
        from slack_sdk import WebClient
        from slack_sdk.errors import SlackApiError

        client = WebClient(token=SLACK_BOT_TOKEN)
        blocks = format_slack_message(alert_name, service, severity, analysis, metrics, fired_at)
        client.chat_postMessage(
            channel=channel,
            text=f"Incident alert: {alert_name} on {service}",
            blocks=blocks,
        )
        return True
    except Exception as exc:
        log.error("slack_send_failed", error=str(exc))
        return False


# ── HTTP API ───────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "mock_mode": MOCK_MODE,
        "llm_provider": LLM_PROVIDER,
        "slack_configured": bool(SLACK_BOT_TOKEN),
    }


@app.post("/webhook")
async def handle_alertmanager_webhook(request: Request):
    payload = await request.json()
    log.info("webhook_received", status=payload.get("status"), mock_mode=MOCK_MODE)

    if payload.get("status") != "firing":
        return {"status": "ignored", "reason": "not firing"}

    results = []
    for alert in payload.get("alerts", []):
        labels = alert.get("labels", {})
        alert_name = labels.get("alertname", "Unknown")
        severity = labels.get("severity", "warning")
        service = labels.get("job", labels.get("service", "unknown"))
        fired_at = alert.get("startsAt", datetime.now(timezone.utc).isoformat())

        logs = await get_loki_logs(service)
        metrics = await get_prometheus_metrics(service)
        deployments = await get_recent_deployments(service)
        pod_events = await get_pod_events(service)

        analysis = await analyse_incident(
            alert_name, service, severity, logs, metrics, deployments, pod_events, fired_at
        )
        print_console_report(alert_name, service, severity, analysis, metrics, fired_at)
        slack_ok = await post_to_slack(
            SLACK_INCIDENT_CHANNEL, alert_name, service, severity, analysis, metrics, fired_at
        )
        results.append(
            {
                "alert": alert_name,
                "service": service,
                "confidence": analysis.get("confidence"),
                "slack_posted": slack_ok,
                "likely_cause": analysis.get("likely_cause"),
            }
        )

    return {"status": "processed", "results": results}


@app.post("/slack/commands")
async def handle_slash_command(request: Request):
    """
    Path C — Slack slash commands.

    TODO: implement /status, /logs, /deploys, /rollback (two-step confirm).
    Until then, return a helpful stub so Slack doesn't show a silent failure.
    """
    form = await request.form()
    command = form.get("command", "")
    text = form.get("text", "").strip()
    return JSONResponse(
        {
            "response_type": "ephemeral",
            "text": (
                f"`{command} {text}` received. "
                "Implement this handler in bot.py (see project README Path C)."
            ),
        }
    )


if __name__ == "__main__":
    if MOCK_MODE:
        log.info("starting_in_mock_mode")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
