# Day 1 — for app teams using this golden path

Hand this to a teammate who has never seen the platform. If they still ping you
for "how do I start?", the docs failed — not the teammate.

## What you get

A Python HTTP service with:

- `/health` and `/ready`
- non-root container image
- Docker Compose for laptop
- Kubernetes manifests (optional Path B)
- a short runbook and catalog stub

## Steps

1. Clone / open the `devops-to-ai` repo (or your fork).
2. From `Phase06_Platform_Engineering/projects/golden-path-template/`:

```bash
./scripts/new_service.sh YOUR-SERVICE-NAME
cd services/YOUR-SERVICE-NAME
docker compose up --build
```

3. Check:

```bash
curl -s http://localhost:8080/health
```

4. Fill in ownership:

- `catalog-info.yaml` → owner
- `docs/runbook.md` → on-call / Slack

5. Build features in `app/` — don't invent a parallel Dockerfile unless you must.

## Need something the path doesn't support?

Open a platform request (or PR against `skeleton/`) instead of quietly forking forever.
Document the escape hatch in your runbook.
