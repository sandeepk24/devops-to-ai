# GitOps & ArgoCD cheatsheet

**Use this when:** you want Git to drive what's running in the cluster — not kubectl from someone's laptop.  
**One-liner:** Git is truth; ArgoCD reconciles the cluster to match.

---

## Mental model

```
Developer merges to Git (manifests / Helm values)
        ↓
ArgoCD polls repo (or webhook fires)
        ↓
Diff: Git desired state vs cluster actual state
        ↓
Sync (auto or manual) → cluster updated
        ↓
Someone kubectl edit's anyway? → ArgoCD reverts (if self-heal on)
```

---

## Install (kind / k3d lab)

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# UI (pick one)
kubectl port-forward svc/argocd-server -n argocd 8080:443
# initial admin password:
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
```

---

## Application manifest (minimal)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: payments-service
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/you/observability-stack.git
    targetRevision: main
    path: k8s/apps/payments-service
  destination:
    server: https://kubernetes.default.svc
    namespace: demo
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

| Field | Meaning |
|---|---|
| `automated` | Sync on Git changes |
| `selfHeal` | Undo manual cluster edits |
| `prune` | Delete resources removed from Git |

---

## CLI you'll actually use

```bash
argocd login localhost:8080 --insecure
argocd app list
argocd app get payments-service
argocd app sync payments-service
argocd app diff payments-service
argocd app history payments-service
argocd app rollback payments-service 2
```

---

## Sync policies — pick on purpose

| Mode | When |
|---|---|
| Manual sync | Learning, or prod with approval |
| Auto sync | Dev/staging, fast feedback |
| Self-heal | Prevent drift — great for capstone demo |
| Prune | Remove orphaned resources when Git deletes them |

---

## Drift demo (capstone proof)

```bash
# After ArgoCD manages a Deployment:
kubectl -n demo edit deployment payments-service
# Change replicas or an env var

# Watch ArgoCD revert within a few minutes (self-heal) or:
argocd app sync payments-service
```

---

## App of Apps (pattern to know)

One ArgoCD Application points at a folder of other Application YAMLs. Bootstraps a whole cluster from one `kubectl apply`. You don't need this on day one — just know the name.

---

## Common footguns

| Symptom | Likely cause |
|---|---|
| OutOfSync forever | K8s adds default fields; use `ignoreDifferences` or sync options |
| Sync failed | Invalid YAML, missing namespace, image pull errors |
| Wrong version deployed | Wrong `targetRevision` or path |
| Secrets in Git | Use Sealed Secrets / External Secrets — not plain text |

---

## Phase 02 tip

Get **local observability** working in Compose first. Add ArgoCD on kind when metrics/logs/traces already make sense — otherwise you're debugging three things at once.

---

*Part of [devops-to-ai](../../README.md) — Phase 02: Cloud Native Operations*
