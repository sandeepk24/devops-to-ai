# Prompt engineering cheatsheet for DevOps

Patterns, templates, and anti-patterns for getting reliable output from LLMs in infrastructure work.

---

## The core formula

```
[Role]       Who the AI should be
[Context]    Your environment, constraints, conventions
[Task]       Exactly what you want
[Format]     How the output should be structured
[Guardrails] What to avoid, flag, or refuse
```

Not every prompt needs all five. Simple tasks need less. High-stakes infrastructure generation needs all of them.

---

## Prompting techniques

### Zero-shot
Ask directly. Works for well-defined tasks where the AI already has strong training signal.

```
Explain what this Kubernetes event means and what to do about it:
"Back-off restarting failed container payments in pod payments-7d9f8b-xk2p9"
```

### Few-shot
Provide examples of input → output before your actual request. Use when you need a specific format or style the AI might not infer.

```
Convert these Prometheus alert rules to include a 'team' label.

Example:
Input:
  - alert: HighCPU
    expr: cpu_usage > 80
    for: 5m

Output:
  - alert: HighCPU
    expr: cpu_usage > 80
    for: 5m
    labels:
      severity: warning
      team: platform

Now convert these rules:
[your rules here]
```

### Chain-of-thought
Ask the AI to reason step by step before giving the answer. Dramatically improves accuracy for diagnostic and debugging tasks.

```
A deployment to production failed. Before telling me what to do, reason through the
possible causes in order of likelihood given these symptoms:
  - Pods are in CrashLoopBackOff
  - Last deployment was 20 minutes ago
  - Error in logs: "connection refused to postgres:5432"
  - Database pod is Running

Walk through each possible cause, then tell me the single most likely root cause
and the exact command to verify it.
```

### Role prompting
Assign a specific expert persona. Works well for security reviews and architecture decisions.

```
You are a senior platform engineer at a financial services company where all
infrastructure must comply with SOC2 Type II. Review this Terraform IAM policy
and flag any violations of least-privilege. For each issue, cite the specific
permission that is too broad and suggest a minimal replacement.

[paste policy here]
```

### Structured output
Ask for JSON or a specific schema. Essential when you're parsing AI output in code.

```
Analyse these application logs and return ONLY a JSON object with this exact schema:
{
  "severity": "critical|high|medium|low",
  "likely_cause": "one sentence",
  "affected_component": "service or component name",
  "recommended_actions": ["action 1", "action 2", "action 3"],
  "confidence": "high|medium|low",
  "needs_human_escalation": true|false
}

Do not include any text outside the JSON object.

Logs:
[paste logs here]
```

---

## Infrastructure code generation prompts

### Terraform resource

```
Generate a Terraform resource for [resource type] with these requirements:
- Provider: [aws|gcp|azure]
- [requirement 1]
- [requirement 2]
- [requirement 3]
- Tags: environment=[env], team=[team], managed_by=terraform
- Follow these naming conventions: [your conventions]

Security requirements:
- [security requirement 1]
- [security requirement 2]

Output ONLY the Terraform HCL, no explanation. Include a variables block for
any values that should be configurable.
```

**Example:**
```
Generate a Terraform resource for an AWS S3 bucket with these requirements:
- Versioning enabled
- Server-side encryption with AES-256
- Public access blocked on all four settings
- Lifecycle rule: transition to STANDARD_IA after 30 days, GLACIER after 90 days, delete after 365 days
- Access logging enabled to a separate bucket named ${var.bucket_name}-logs
- Tags: environment=production, team=platform, managed_by=terraform

Output ONLY the Terraform HCL. Include a variables block for bucket_name and region.
```

### Kubernetes manifest

```
Write a Kubernetes [Deployment|StatefulSet|CronJob] manifest for [app name]:
- Image: [registry/image:tag]
- Replicas: [n]
- CPU limit: [Xm], CPU request: [Xm]
- Memory limit: [XMi], Memory request: [XMi]
- Liveness probe: [endpoint], initial delay [n]s
- Readiness probe: [endpoint], initial delay [n]s
- Environment variables from ConfigMap: [name]
- Secrets from Secret: [name]
- Runs as non-root, UID [n]
- [any other requirements]

Output ONLY the YAML. Use apiVersion apps/v1.
```

### GitHub Actions pipeline

```
Write a GitHub Actions workflow that:
- Triggers on: [push to main | pull_request | schedule]
- Uses Ubuntu latest runner
- Jobs (in order, each depending on the previous):
  1. [job name]: [what it does]
  2. [job name]: [what it does]
  3. [job name]: [what it does]
- Secrets needed: [SECRET_1], [SECRET_2]
- [any caching requirements]
- [any environment or deployment requirements]

Output ONLY the workflow YAML. Use actions/checkout@v4.
```

### Dockerfile

```
Write a multi-stage Dockerfile for a [Python|Go|Node] application:
- Base image for build stage: [image:tag]
- Base image for runtime stage: [image:tag] (prefer distroless or alpine)
- Build steps: [describe build process]
- Final image must:
  - Run as non-root user (UID 1000)
  - Be under [size]MB
  - Expose port [n]
  - Have a HEALTHCHECK using [endpoint]
  - Set PYTHONUNBUFFERED=1 (if Python)

Output ONLY the Dockerfile.
```

---

## Incident analysis prompt templates

### Alert triage

```
You are an SRE responding to a production alert. Analyse the following context
and provide a structured diagnosis.

ALERT:
Name: {alert_name}
Severity: {severity}
Service: {service_name}
Fired at: {timestamp}
Labels: {labels}

RECENT LOGS (last 30 minutes, error level only):
{logs}

CURRENT METRICS:
- Error rate: {error_rate}%
- p99 latency: {p99_latency}ms
- Request rate: {rps} req/s
- CPU usage: {cpu}%
- Memory usage: {memory}%

RECENT DEPLOYMENTS:
{deployments}

POD EVENTS:
{pod_events}

Respond with ONLY this JSON structure:
{
  "summary": "2-3 sentence plain English summary of what is happening",
  "likely_cause": "the single most likely root cause",
  "confidence": "high|medium|low",
  "top_checks": ["check 1", "check 2", "check 3"],
  "immediate_actions": ["action 1", "action 2"],
  "related_runbook": "name of applicable runbook or null",
  "needs_escalation": true|false,
  "escalation_reason": "reason if needs_escalation is true, else null"
}
```

### Log analysis

```
Analyse these application logs and identify:
1. The primary error or issue
2. When it started (timestamp of first occurrence)
3. Whether it is getting better or worse over time
4. Any patterns — is it affecting specific users, endpoints, or operations?
5. Any recent changes visible in the logs that might have caused it

Logs:
{logs}

Be specific. Reference line numbers or timestamps where relevant.
If you cannot determine something with confidence, say so explicitly.
```

### Post-incident review assistance

```
Help me write a post-incident review (PIR) for the following incident.

Incident summary:
{incident_summary}

Timeline of events:
{timeline}

Contributing factors identified:
{contributing_factors}

Actions taken to resolve:
{resolution_actions}

Write a PIR with these sections:
1. Executive summary (3 sentences, non-technical)
2. Impact (who was affected, for how long, estimated impact)
3. Timeline (format as a table: time | event | who)
4. Root cause analysis (use 5 Whys format)
5. Contributing factors
6. What went well
7. Action items (format as a table: action | owner | due date | priority)

Tone: factual, blameless, focused on systems not people.
```

---

## Security review prompts

### Terraform security review

```
You are a security engineer reviewing infrastructure code for a production system
that handles sensitive customer data.

Review this Terraform code and identify:
1. IAM permissions that violate least-privilege (flag any use of "*")
2. Network rules that are overly permissive (flag 0.0.0.0/0 ingress)
3. Missing encryption (storage, transit, secrets)
4. Resources that could expose data if misconfigured
5. Missing logging or audit trails
6. Any other security concerns

For each issue: describe the risk, the specific line or resource, and the fix.
Format as a numbered list ordered by severity (Critical → High → Medium → Low).

Code:
{terraform_code}
```

### Kubernetes manifest review

```
Review this Kubernetes manifest for security issues and best practice violations.

Check for:
- Containers running as root or with privileged: true
- Missing resource limits (CPU and memory)
- Images using :latest tag
- Secrets mounted as environment variables instead of volumes
- Missing readiness/liveness probes
- Service accounts with excessive permissions
- Host network or host PID usage
- Missing pod security context

For each issue: the field name, the risk, and the correct value.

Manifest:
{manifest_yaml}
```

---

## Anti-patterns — what NOT to do

```
# Too vague — AI has no idea what "production-ready" means to you
"Write production-ready Terraform for AWS"

# Missing constraints — will generate insecure defaults
"Write a security group for my web server"

# No format specified — will dump prose when you want YAML
"Create a Kubernetes deployment"

# Asking for too much at once — quality degrades
"Write the entire infrastructure for a microservices app with 10 services,
a database, a message queue, monitoring, and CI/CD"

# Trusting without verifying — the fastest way to break production
[AI generates IAM policy] → immediately applying without reading it
```

---

## Red flags in AI-generated infrastructure code

Always check for these before applying anything AI generates:

```
Terraform:
  ✗  resource "*" or action "*" in IAM policies
  ✗  ingress 0.0.0.0/0 on sensitive ports (22, 3306, 5432, 6379)
  ✗  force_destroy = true on S3 buckets or databases
  ✗  Hardcoded credentials, even in comments
  ✗  Missing backend configuration for state
  ✗  count = 0 accidentally left in (silently destroys resources)

Kubernetes:
  ✗  privileged: true in securityContext
  ✗  runAsRoot: true or missing runAsNonRoot: true
  ✗  Missing resource limits (pods can consume all node resources)
  ✗  image: myapp:latest (unpredictable, breaks reproducibility)
  ✗  hostNetwork: true or hostPID: true
  ✗  Secrets as env vars (visible in pod spec, logs)

GitHub Actions:
  ✗  pull_request_target with untrusted code checkout (RCE risk)
  ✗  Hardcoded secrets in env blocks
  ✗  permissions: write-all (too broad)
  ✗  Pinning actions by branch (e.g. @main) instead of SHA
```

---

## Shell aliases for AI-assisted debugging

Add these to your `~/.zshrc` or `~/.bashrc`:

```bash
# Explain a command before running it
explain() {
  echo "Explain what this command does in plain English, including any risks: $*" \
    | llm   # replace with your preferred CLI tool (e.g. 'claude', 'sgpt', 'llm')
}

# Pipe any output to AI for explanation
alias ai-explain="llm 'Explain this output in plain English and identify any issues:'"

# Review a git diff before committing
alias ai-review="git diff --staged | llm 'Review this code diff. Flag bugs, security issues, and missing error handling. Be concise.'"

# Explain a kubectl error
alias k-explain="kubectl describe pod \$1 | llm 'This pod has a problem. Explain what is wrong and give me the exact kubectl command to investigate further.'"

# Debug a failing service
debug-service() {
  local service=$1
  {
    echo "=== Recent logs ==="
    kubectl logs -l app=$service --tail=50 --since=30m
    echo "=== Pod events ==="
    kubectl get events --field-selector involvedObject.name=$service --sort-by='.lastTimestamp'
  } | llm "This service is having problems. What is wrong and what should I do?"
}
```

---

*Part of [devops-to-ai](../../README.md) — Phase 03: AI-Augmented DevOps*
