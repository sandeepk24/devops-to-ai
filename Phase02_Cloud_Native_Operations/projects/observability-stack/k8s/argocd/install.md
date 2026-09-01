# ArgoCD on a local cluster (Phase 02 stretch)

Do this **after** the Docker Compose stack works. Otherwise you're debugging observability *and* GitOps at once.

## Prerequisites

- kind or k3d cluster with kubectl context set
- Helm charts for the three services (copy patterns from Phase 01)

## Install ArgoCD

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

kubectl port-forward svc/argocd-server -n argocd 8080:443
# Login: admin / password from:
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
```

## Wire your repo

1. Push manifests under `k8s/apps/` to GitHub
2. Create an `Application` per service (see [GitOps cheatsheet](../../cheatsheets/gitops.md))
3. Enable `selfHeal: true` for the drift demo

## Prove self-healing

```bash
kubectl -n demo edit deployment payments-service
# change replicas — watch ArgoCD revert
```

## Observability on Kubernetes

Replace Compose scrape targets with Prometheus `kubernetes_sd_configs` or install `kube-prometheus-stack` and add ServiceMonitor resources. The Phase 02 [observability cheatsheet](../../cheatsheets/observability.md) has a commented k8s scrape example in `prometheus.yml`.
