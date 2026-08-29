# Kubernetes & kubectl cheatsheet

**Use this when:** deploying apps, debugging pods, or checking rollouts.  
**Start every incident with:** `kubectl get pods` → `kubectl describe pod <name>` → `kubectl logs <name>`

---

## Mental model

```
You declare desired state (YAML)
        ↓
API server stores it
        ↓
Controllers / scheduler make reality match
        ↓
If something dies, Kubernetes starts another
```

You rarely manage containers by hand. You manage **Deployments**, and Kubernetes manages pods.

---

## Cluster access

```bash
kubectl cluster-info
kubectl get nodes
kubectl config current-context
kubectl config get-contexts
```

**Local practice clusters:**

```bash
# kind
kind create cluster --name phase01
kind delete cluster --name phase01

# k3d
k3d cluster create phase01
k3d cluster delete phase01
```

---

## Everyday commands

```bash
kubectl get pods -A
kubectl get deploy,svc,ingress -n myapp
kubectl get pods -o wide
kubectl get pods -w                          # watch

kubectl describe pod POD
kubectl logs POD
kubectl logs deploy/API --tail=100 -f
kubectl logs POD -c SIDECAR                  # multi-container pod

kubectl exec -it POD -- sh
kubectl port-forward svc/API 8080:80
```

---

## Apply & change things

```bash
kubectl apply -f deployment.yaml
kubectl apply -f manifests/                  # whole folder
kubectl diff -f deployment.yaml              # what would change

kubectl scale deploy/API --replicas=3
kubectl set image deploy/API api=ghcr.io/you/api:abc1234
kubectl rollout status deploy/API
kubectl rollout history deploy/API
kubectl rollout undo deploy/API
```

Prefer `apply` (declarative) over one-off `create` for anything you want to keep.

---

## Objects you'll use constantly

| Object | Job |
|---|---|
| Pod | Running container(s) — usually created by a Deployment |
| Deployment | Keeps N pods alive; rolling updates |
| Service | Stable DNS + load balance to pods |
| Ingress | HTTP(S) entry from outside the cluster |
| ConfigMap | Non-secret config |
| Secret | Sensitive config (still base64 — treat carefully) |
| Namespace | Isolation bucket for resources |

**Service types (quick):**
- `ClusterIP` — internal only (default)
- `NodePort` — expose on each node (fine for learning)
- `LoadBalancer` — cloud LB (or local kind/k3d equivalents)

---

## Debug flowchart

```
Pod not Ready / CrashLoopBackOff?
│
├─ kubectl describe pod POD
│     Events at the bottom — read them
├─ kubectl logs POD
│     App error? Bad config? Missing file?
├─ ImagePullBackOff?
│     Wrong tag, private registry auth, typo
├─ Pending forever?
│     Resources / node selectors / PVC issues
└─ Running but 502 from outside?
      Service selector mismatch, wrong port, Ingress path
```

**Probes (put these on real apps):**
- **Liveness** — restart me if I'm stuck
- **Readiness** — don't send traffic until I'm ready

Bad probes cause flapping. Start simple (`/health`, `/ready`).

---

## Resources

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "256Mi"
```

Requests = scheduling guarantee. Limits = hard cap. Missing requests is how noisy neighbours steal the node.

---

## Helm quick hits

```bash
helm create mychart
helm lint ./mychart
helm template myrelease ./mychart -f values-dev.yaml
helm upgrade --install myrelease ./mychart -n myapp --create-namespace -f values-dev.yaml
helm rollback myrelease 1
helm uninstall myrelease -n myapp
```

---

## YAML skeleton (Deployment + Service)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: ghcr.io/you/api:latest
          ports:
            - containerPort: 8080
          readinessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: api
spec:
  selector:
    app: api
  ports:
    - port: 80
      targetPort: 8080
```

Selector labels on the Service **must** match pod labels. Mismatch = silent empty endpoints.

---

*Part of [devops-to-ai](../../README.md) — Phase 01: Core DevOps*
