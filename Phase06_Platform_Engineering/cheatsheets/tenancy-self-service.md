# Tenancy & self-service cheatsheet

**Use this when:** you're tempted to either (a) open the cluster to everyone or (b) require a ticket for every namespace.  
**Rule of thumb:** self-service inside a fence. The fence is quotas, policies, and "who owns this."

---

## Simple tenancy model (good enough to start)

```
cluster
  └── namespace: team-a-payments    ← one service or one team
  └── namespace: team-b-checkout
```

Labels that save you later:

```yaml
metadata:
  labels:
    app.kubernetes.io/name: payments-api
    app.kubernetes.io/part-of: checkout
    team: payments
```

---

## Guardrails that belong on the paved road

| Control | Why |
|---|---|
| ResourceQuota / LimitRange | Stops one team from eating the node |
| No privileged pods (Phase 05) | Admission > wiki reminders |
| Allowed image registries | Supply chain basics |
| Who can create Namespaces | Often platform-only at first |

Self-service examples that are usually safe early:

- Scaffold a new service from the golden path
- Deploy to *dev* namespace via CI
- Open a PR that updates their own Helm values

Usually needs approval:

- Prod promote
- Public ingress / raw LoadBalancer
- Cluster-scoped RBAC changes

---

## Multi-tenancy levels (interview sketch)

1. **Soft** — namespaces + culture  
2. **Harder** — quotas, network policies, Pod Security  
3. **Hard** — separate clusters / accounts per tenant  

Juniors: nail (1)→(2) on kind before designing (3).

---

## Platform ticket smell test

If the same request appears weekly ("please create a pipeline"), that's a golden-path gap — not a staffing plan.

---

## Lab pointer

Phase 06 Path B manifests use a dedicated namespace per scaffolded service. Quotas are documented as stretch in the project README.
