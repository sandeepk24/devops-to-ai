# Golden paths cheatsheet

**Use this when:** you're deciding what "the blessed way" to create a new service should include.  
**Rule of thumb:** if a junior still needs three Slack threads to get to `/health`, the path isn't paved yet.

---

## Paved road vs dirt path

| Paved (golden path) | Dirt (escape hatch) |
|---|---|
| Default for 80% of services | Special cases, with eyes open |
| Secure-ish defaults on | You accept extra risk/review |
| Docs + template maintained | You own the snowflake |
| Platform team updates the skeleton | You chase CVE upgrades alone |

Escape hatches are fine. Making the escape hatch the only documented path is not.

---

## What to bake into a service template

Minimum that earns the name "golden path":

- [ ] App skeleton with `/health` (and ideally `/ready`)
- [ ] Multi-stage Dockerfile, non-root user
- [ ] Compose (or equivalent) for laptop day-1
- [ ] K8s manifests or Helm with requests/limits stubs
- [ ] CI workflow stub (lint/test/build shape)
- [ ] Short runbook: how to run, how to deploy, who to page
- [ ] Placeholder for metrics/logs (even if "TODO: wire OTel")

Nice later: SBOM/scan steps (Phase 05), NetworkPolicy, HPA, Backstage `catalog-info.yaml`.

---

## Version the path

Treat the template like a product:

```
skeleton/ v1  →  teams scaffold from it
         v2  →  changelog: "non-root now required"
```

If you change the skeleton and never tell consumers, you've created silent drift.

---

## Anti-patterns

- Template that only works on one person's laptop paths
- 15 optional flags before anything runs
- "Just copy prod-service-x" as the official docs
- Security bolted on after the template is already viral

---

## Lab pointer

Phase 06: `projects/golden-path-template/scripts/new_service.sh`
