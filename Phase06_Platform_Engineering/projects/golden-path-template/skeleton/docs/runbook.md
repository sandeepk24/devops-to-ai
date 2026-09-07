# Day-2 ops for __SERVICE_NAME__ — keep this short enough that people read it.

## Run locally

```bash
docker compose up --build
curl -s http://localhost:8080/health
```

## Deploy (kind / Path B)

```bash
# From golden-path-template root:
./scripts/deploy_kind.sh __SERVICE_NAME__
kubectl -n __SERVICE_NAME__ port-forward svc/__SERVICE_NAME__ 8080:8080
```

## Ownership

- **Team / owner:** (fill in)
- **On-call:** (fill in)
- **Slack:** (fill in)

## SLOs (stubs)

- Availability: (e.g. 99.9% monthly on `/health`)
- Latency: (fill when you have real traffic)

## Rollback

1. Redeploy previous image tag / Git SHA  
2. Confirm `/health` and `/ready`  
3. Tell on-call what changed  

## When to leave the golden path

Only when the paved road can't meet a real requirement — and document why.
