# Policy-as-code cheatsheet

**Use this when:** CI might be skipped or misconfigured and you still need the cluster to refuse dangerous pods.  
**Rule of thumb:** start with one high-value rule (no privileged containers). Expand after that rule is boringly reliable.

---

## Where policy sits

```
Developer → CI gates → registry → deploy → Admission controller → API server
                                              ↑
                                         Kyverno / OPA Gatekeeper / ValidatingAdmissionPolicy
```

CI is the friendly guard at the door. Admission is the lock on the vault.

---

## Privileged pods — the junior classic

```yaml
securityContext:
  privileged: true   # almost never what you want for an app
```

Privileged ≈ "this container can do host-level things." Fine for some system agents; almost never for your API.

---

## Kyverno policy shape (ClusterPolicy)

See the lab file `policy/disallow-privileged.yaml`. Conceptually:

- Match Pods (and controllers that create them)
- Validate `spec.containers[*].securityContext.privileged` is not `true`
- `validationFailureAction: Enforce` (or `Audit` while learning)

Dry-run habit: install Kyverno → `kubectl apply --dry-run=server` or Kyverno's test/apply CLI before Enforce in shared clusters.

---

## Path A without a cluster

The lab's `scripts/check_manifests.sh` greps manifests for `privileged: true`. That is **not** a replacement for admission control — it's a teaching brake so you can fail fast on a laptop.

Path B: install Kyverno on kind/k3d, run `./scripts/wait_kyverno.sh`, apply `policy/disallow-privileged.yaml`, then `kubectl apply -f k8s/deployment-bad-privileged.yaml` — expect deny.

---

## Other first policies (after privileged)

- Require non-root (`runAsNonRoot: true`)
- Disallow hostNetwork / hostPID
- Require resource requests/limits (noisy — introduce carefully)
- Only allow images from your registry

---

## Useful links

- [Kyverno docs](https://kyverno.io/docs/)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- Phase 05 lab: `policy/` + `k8s/deployment-*.yaml`
