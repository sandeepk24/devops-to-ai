# GitHub Actions cheatsheet

**Use this when:** automating lint, test, build, and deploy from Git.  
**Habit:** every repo gets CI early — even if it's only lint + test.

---

## Mental model

```
Event (push, PR, manual)
   → Workflow (.github/workflows/*.yml)
        → Job (runs on a runner / VM)
             → Steps (actions or shell commands)
```

Jobs can depend on each other with `needs`. Steps in a job run in order on the same machine.

---

## Minimal workflow

```yaml
name: ci

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install -r requirements.txt
      - run: pytest -q
```

---

## Pipeline shape for Phase 01

```yaml
name: microservice-pipeline

on:
  push:
    branches: [main]
  pull_request:

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "add ruff/flake8/golangci-lint here"

  test:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "pytest / go test here"

  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - run: echo "docker build + push to GHCR here"

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - run: echo "helm upgrade --install ... here"
```

`deploy` only on `main` keeps PR noise from touching your cluster.

---

## Secrets & env

```yaml
env:
  APP_ENV: staging

steps:
  - name: login to GHCR
    run: echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
```

- Store kubeconfig, cloud keys, registry passwords in **GitHub Secrets**
- Never echo secrets in logs
- Prefer `GITHUB_TOKEN` when it has enough permission
- Limit `permissions:` on jobs (least privilege)

---

## Useful building blocks

```yaml
# Manual run button in the Actions UI
on:
  workflow_dispatch:

# Only certain paths
on:
  push:
    paths:
      - "app/**"
      - "Dockerfile"

# Matrix
strategy:
  matrix:
    python-version: ["3.11", "3.12"]
```

**Caching:** `actions/setup-python` / `setup-node` often handle caches via `cache: pip` / `cache: npm`.

**Local dry-run:** [act](https://github.com/nektos/act) — great for iterating without burning CI minutes.

---

## Docker build + push (GHCR sketch)

```yaml
- uses: docker/setup-buildx-action@v3
- uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
- uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: |
      ghcr.io/${{ github.repository_owner }}/myapp:${{ github.sha }}
      ghcr.io/${{ github.repository_owner }}/myapp:latest
```

Tag with git SHA for rollbacks. `latest` alone is how you lose track of what's running.

---

## Deploy from CI

Typical pattern:

1. Build pushes `image:sha`
2. Deploy job checks out repo
3. Writes kubeconfig from `secrets.KUBE_CONFIG` (base64)
4. Runs `helm upgrade --install ... --set image.tag=$SHA`

For **kind on a laptop**, CI deploy is optional — document a manual `helm upgrade` and run CI for lint/test/build first. Wire deploy when you have a reachable cluster.

---

## Branch protection (do this)

In the GitHub repo settings:

- Require PR before merge to `main`
- Require the `test` (and ideally `lint`) checks to pass

That's how "green main" stays true.

---

## Common footguns

| Symptom | Likely cause |
|---|---|
| Works locally, fails in CI | Missing deps, different Python/Go version, relying on your laptop files |
| Can't push to GHCR | Missing `packages: write` permission |
| Secret is empty | Typo in secret name; secrets not available to forks the same way |
| Deployed wrong image | Used `latest` instead of SHA |

---

*Part of [devops-to-ai](../../README.md) — Phase 01: Core DevOps*
