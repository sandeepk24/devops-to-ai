"""
AI-powered incident response bot — Phase 03 capstone project.

Receives Alertmanager webhooks, gathers context from Loki/Prometheus/k8s,
sends to Claude API for analysis, posts structured diagnosis to Slack.

Usage:
    pip install -r requirements.txt
    cp .env.example .env && edit .env
    python bot.py
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Optional

import httpx
import structlog
import uvicorn
from anthropic import Anthropic
from fastapi import FastAPI, Request
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# ── configuration ──────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_INCIDENT_CHANNEL = os.environ.get("SLACK_INCIDENT_CHANNEL", "#incidents")
PROMETHEUS_URL = os.environ.get("PROMETHEUS_URL", "http://prometheus:9090")
LOKI_URL = os.environ.get("LOKI_URL", "http://loki:3100")
KUBECONFIG = os.environ.get("KUBECONFIG", os.path.expanduser("~/.kube/config"))

# ── logging ────────────────────────────────────────────────────────────────────
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)
log = structlog.get_logger()

# ── clients ────────────────────────────────────────────────────────────────────
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
slack_client = WebClient(token=SLACK_BOT_TOKEN)

app = FastAPI(title="incident-response-bot")


# ── context gathering ──────────────────────────────────────────────────────────

async def get_loki_logs(service: str, minutes: int = 30) -> str:
    """
    Fetch recent error-level logs for a service from Loki.
    Returns formatted log lines as a string, or an error message.
    """
    # TODO: implement this function
    # Hints:
    # - Loki query API: GET {LOKI_URL}/loki/api/v1/query_range
    # - Parameters: query, start, end, limit
    # - Query: '{app="{service}"} | json | level="error"'
    # - start/end: Unix nanosecond timestamps
    # - Parse the response: data.result[].values[][] = [timestamp, log_line]
    # - Return the last 50 lines as a single string
    # - If Loki is unreachable, return "Loki unavailable — logs not included"
    # - Never let this function raise an exception
    pass


async def get_prometheus_metrics(service: str) -> dict:
    """
    Fetch current golden signal metrics for a service from Prometheus.
    Returns a dict with error_rate, p99_latency, rps, cpu_percent, memory_percent.
    """
    # TODO: implement this function
    # Hints:
    # - Prometheus instant query API: GET {PROMETHEUS_URL}/api/v1/query
    # - Parameter: query (PromQL expression)
    # - Use these queries (replace {service} with the actual service name):
    #
    #   error_rate:
    #     sum(rate(http_requests_total{job="{service}",status=~"5.."}[5m]))
    #     / sum(rate(http_requests_total{job="{service}"}[5m])) * 100
    #
    #   p99_latency (in ms):
    #     histogram_quantile(0.99, sum by(le)(
    #       rate(http_request_duration_seconds_bucket{job="{service}"}[5m])
    #     )) * 1000
    #
    #   rps:
    #     sum(rate(http_requests_total{job="{service}"}[5m]))
    #
    # - Round all values to 2 decimal places
    # - If Prometheus is unreachable, return default dict with None values
    # - Never let this function raise an exception
    pass


async def get_recent_deployments(service: str, limit: int = 5) -> str:
    """
    Fetch recent ArgoCD application sync history for a service.
    Falls back to git log if ArgoCD is not available.
    Returns a formatted string.
    """
    # TODO: implement this function
    # Option A — ArgoCD API:
    #   GET http://argocd-server/api/v1/applications/{service}/resource-tree
    #   GET http://argocd-server/api/v1/applications/{service}/history
    #   Format: "2024-01-15 14:32 UTC | v1.2.3 | deployed by ci-bot"
    #
    # Option B — git log (simpler for local development):
    #   import subprocess
    #   result = subprocess.run(
    #     ["git", "log", "--oneline", f"-{limit}", "--format=%ci %s"],
    #     capture_output=True, text=True
    #   )
    #   return result.stdout
    #
    # Return "No recent deployments found" if neither is available
    pass


async def get_pod_events(service: str) -> str:
    """
    Fetch recent Kubernetes events for pods of a service.
    Returns formatted events as a string.
    """
    # TODO: implement this function
    # Hints:
    # - Use the kubernetes Python client (pip install kubernetes)
    # - from kubernetes import client, config
    # - config.load_kube_config() or config.load_incluster_config()
    # - v1 = client.CoreV1Api()
    # - events = v1.list_namespaced_event(namespace="default",
    #     field_selector=f"involvedObject.name={service}")
    # - Format: "14:32:01 | Warning | BackOff | Back-off restarting failed container"
    # - Return only the last 10 events
    # - If kubernetes is unreachable, return "Kubernetes events unavailable"
    pass


# ── prompt loading ─────────────────────────────────────────────────────────────

def load_prompt(name: str) -> str:
    """Load a prompt template from the prompts/ directory."""
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", f"{name}.txt")
    try:
        with open(prompt_path) as f:
            return f.read()
    except FileNotFoundError:
        log.error("prompt_not_found", name=name, path=prompt_path)
        raise


# ── ai analysis ────────────────────────────────────────────────────────────────

async def analyse_incident(
    alert_name: str,
    service: str,
    severity: str,
    logs: str,
    metrics: dict,
    deployments: str,
    pod_events: str,
) -> dict:
    """
    Send incident context to Claude and get structured diagnosis.
    Returns parsed JSON response or a fallback dict if AI fails.
    """
    # TODO: implement this function
    # Hints:
    # - Load the prompt template: load_prompt("incident-analysis")
    # - Fill in the template variables (alert_name, service, logs, metrics, etc.)
    # - Call the Claude API:
    #     response = anthropic_client.messages.create(
    #         model="claude-opus-4-5",
    #         max_tokens=1024,
    #         messages=[{"role": "user", "content": filled_prompt}]
    #     )
    # - Parse response.content[0].text as JSON
    # - If JSON parsing fails, return a fallback dict:
    #     {"summary": "AI analysis unavailable", "likely_cause": "unknown",
    #      "confidence": "low", "top_checks": [], "immediate_actions": [],
    #      "needs_escalation": True, "escalation_reason": "AI analysis failed"}
    # - Log the raw AI response for debugging
    # - Never let this function raise an exception — incidents must always get a Slack message
    pass


# ── slack formatting ───────────────────────────────────────────────────────────

def format_slack_message(
    alert_name: str,
    service: str,
    severity: str,
    analysis: dict,
    metrics: dict,
    fired_at: str,
) -> list:
    """
    Format the incident analysis as a Slack Block Kit message.
    Returns a list of Slack blocks.
    """
    # TODO: implement this function
    # Use Slack Block Kit (https://api.slack.com/block-kit)
    # The message should include:
    #
    # [Header block]
    #   🚨 CRITICAL: HighErrorRate — payments-service
    #
    # [Section block — metrics]
    #   Error rate: 4.2% | p99 latency: 842ms | RPS: 127
    #
    # [Section block — AI summary]
    #   "Payments service is experiencing elevated error rate due to
    #    timeouts connecting to Stripe API..."
    #
    # [Section block — top checks]
    #   1. Check Stripe status page
    #   2. Review circuit breaker configuration
    #   3. Check recent changes to payment retry logic
    #
    # [Section block — immediate actions]
    #   → Check Stripe status page: https://status.stripe.com
    #   → kubectl logs -l app=payments-service --tail=100
    #
    # [Context block]
    #   Fired at: 2024-01-15 02:34 UTC | Confidence: high | AI analysis by Claude
    #
    # Use ⚠️ for warning severity, 🚨 for critical, ℹ️ for info
    pass


async def post_to_slack(
    channel: str,
    alert_name: str,
    service: str,
    severity: str,
    analysis: dict,
    metrics: dict,
    fired_at: str,
) -> bool:
    """Post the incident analysis to Slack. Returns True on success."""
    blocks = format_slack_message(alert_name, service, severity, analysis, metrics, fired_at)

    try:
        slack_client.chat_postMessage(
            channel=channel,
            text=f"Incident alert: {alert_name} on {service}",   # fallback text
            blocks=blocks,
        )
        log.info("slack_message_sent", channel=channel, alert=alert_name, service=service)
        return True
    except SlackApiError as e:
        log.error("slack_send_failed", error=str(e), channel=channel)
        return False


# ── webhook handler ────────────────────────────────────────────────────────────

@app.post("/webhook")
async def handle_alertmanager_webhook(request: Request):
    """
    Receive Alertmanager webhook payload and trigger incident analysis.

    Alertmanager payload format:
    {
      "version": "4",
      "status": "firing",
      "alerts": [
        {
          "status": "firing",
          "labels": {
            "alertname": "HighErrorRate",
            "severity": "critical",
            "job": "payments-service"
          },
          "annotations": { "summary": "...", "description": "..." },
          "startsAt": "2024-01-15T02:34:00Z"
        }
      ]
    }
    """
    payload = await request.json()
    log.info("webhook_received", status=payload.get("status"))

    if payload.get("status") != "firing":
        return {"status": "ignored", "reason": "not firing"}

    for alert in payload.get("alerts", []):
        labels = alert.get("labels", {})
        alert_name = labels.get("alertname", "Unknown")
        severity = labels.get("severity", "warning")
        service = labels.get("job", labels.get("service", "unknown"))
        fired_at = alert.get("startsAt", datetime.utcnow().isoformat())

        log.info("processing_alert", alert=alert_name, service=service, severity=severity)

        # TODO: gather all context concurrently (use asyncio.gather for speed)
        logs = await get_loki_logs(service)
        metrics = await get_prometheus_metrics(service)
        deployments = await get_recent_deployments(service)
        pod_events = await get_pod_events(service)

        # TODO: call analyse_incident() with all gathered context

        # TODO: call post_to_slack() with the analysis

    return {"status": "processed", "alerts": len(payload.get("alerts", []))}


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# ── slack slash commands ───────────────────────────────────────────────────────

@app.post("/slack/commands")
async def handle_slash_command(request: Request):
    """
    Handle Slack slash commands: /status, /logs, /deploys, /rollback

    Slack sends commands as form-encoded POST requests with fields:
      command, text, user_id, user_name, channel_id, response_url
    """
    form = await request.form()
    command = form.get("command", "")
    text = form.get("text", "").strip()
    user = form.get("user_name", "unknown")

    log.info("slash_command", command=command, text=text, user=user)

    if command == "/status":
        # TODO: implement /status <service>
        # 1. Get metrics from Prometheus for the service
        # 2. Get pod count from Kubernetes
        # 3. Return a formatted Slack message with current health
        return {"text": f"TODO: implement /status for {text}"}

    elif command == "/logs":
        # TODO: implement /logs <service> [minutes]
        # Parse text as "<service> [minutes]"
        # Default minutes = 30
        # Get logs from Loki, return last 20 lines
        return {"text": f"TODO: implement /logs for {text}"}

    elif command == "/deploys":
        # TODO: implement /deploys <service>
        # Get last 5 deployments from ArgoCD or git
        # Return as a formatted table
        return {"text": f"TODO: implement /deploys for {text}"}

    elif command == "/rollback":
        # TODO: implement /rollback <service>
        # IMPORTANT: this must be a two-step process:
        # Step 1: Show what the rollback would do and ask for confirmation
        # Step 2: On confirmation, execute the rollback via ArgoCD
        # Never execute a rollback without explicit human confirmation
        return {"text": f"TODO: implement /rollback for {text}"}

    return {"text": f"Unknown command: {command}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
