# IDP basics cheatsheet

**Use this when:** someone says "we need Backstage" and you need to separate product from UI.  
**Rule of thumb:** an Internal Developer Platform is the *interface* to your paved roads. A catalog with three empty cards is not a platform.

---

## What an IDP is

```
Engineer → (portal / CLI / API / docs) → paved actions
              create service
              get logs / metrics links
              request env / secrets (guardrailed)
              see ownership / runbooks
```

**IDP v0** can be: well-kept docs + `new_service.sh` + CI templates + a SCORECARD.md.  
**IDP v1** might add: Backstage, Port, humanitec-style abstractions, etc.

---

## What an IDP is not

- A dumping ground for every internal URL
- A replacement for learning Kubernetes (it *reduces* how often you must)
- "Install Backstage" as a quarterly goal with no golden paths behind it

---

## Catalog stub (Backstage-shaped)

Many IDPs want a small YAML describing the service:

```yaml
# catalog-info.yaml (shape only — works as docs even without Backstage)
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: payments-api
  description: Example service from the golden path
  tags: [python, http]
spec:
  type: service
  lifecycle: experimental
  owner: team-platform-learners
```

Stretch: register it in a real Backstage. Path A: keep the file so ownership is visible in git.

---

## Thin interface checklist

Before buying/building a portal, answer:

1. What are the top 5 actions engineers ask for on Slack?
2. Which of those can be a script/template this month?
3. Who owns the paved road when it breaks?
4. How will you measure adoption?

If you can't answer (4), the portal won't save you.

---

## Useful links

- [Backstage](https://backstage.io/)
- [CNCF Platforms whitepaper](https://tag-app-delivery.cncf.io/whitepapers/platforms/)
- Phase 06 lab: `skeleton/catalog-info.yaml`
