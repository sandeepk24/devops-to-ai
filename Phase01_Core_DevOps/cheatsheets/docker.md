# Docker & Compose cheatsheet

**Use this when:** building images, debugging containers, or wiring up local multi-service apps.  
**Daily trio:** `docker build` → `docker run` → `docker logs`

---

## Mental model (30 seconds)

```
Dockerfile  →  image (immutable layers)  →  container (running + writable layer)
```

When the container stops, the writable layer is gone unless you used a volume.

---

## Build & run

```bash
docker build -t myapp:dev .
docker build -t myapp:dev --target runtime .   # multi-stage: stop at a named stage

docker run --rm -p 8080:8080 myapp:dev
docker run --rm -it myapp:dev sh              # shell into a new container
docker run -d --name api -p 8080:8080 myapp:dev

docker ps                                     # running
docker ps -a                                  # including stopped
docker stop api && docker rm api
```

---

## Debug (you'll live here)

```bash
docker logs api
docker logs -f --tail 100 api
docker exec -it api sh                        # or bash if it exists
docker inspect api                            # config, IPs, mounts
docker stats                                  # CPU / memory live
docker port api                               # published ports
```

**Crash on start?**  
`docker logs` first. Then `docker run --rm -it --entrypoint sh myapp:dev` and poke around.

---

## Images & layers

```bash
docker images
docker history myapp:dev                      # what's in each layer
docker system df                              # disk usage
docker image prune -f                         # clean dangling images
```

**Dockerfile habits that matter:**
- Put least-changing layers first (deps before app code) for cache hits
- Use multi-stage builds for compiled / pip / npm apps
- Add a `.dockerignore` (`.git`, `venv`, `node_modules`, tests you don't need in the image)
- Prefer `USER` non-root in the final stage
- Pin base tags when you can (`python:3.12-slim`, not only `python:latest`)

**Tiny multi-stage sketch (Python):**

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
RUN useradd -r appuser
COPY --from=builder /root/.local /home/appuser/.local
COPY app/ ./app/
ENV PATH=/home/appuser/.local/bin:$PATH
USER appuser
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

---

## Registry

```bash
docker tag myapp:dev ghcr.io/YOU/myapp:abc1234
echo $GITHUB_TOKEN | docker login ghcr.io -u YOU --password-stdin
docker push ghcr.io/YOU/myapp:abc1234
```

Never bake tokens into the image. Pass them at runtime or via your orchestrator secrets.

---

## Compose

```bash
docker compose up --build
docker compose up -d
docker compose logs -f api
docker compose ps
docker compose exec api sh
docker compose down           # stop & remove containers
docker compose down -v        # also wipe named volumes (careful)
```

**Minimal `compose.yaml`:**

```yaml
services:
  api:
    build: .
    ports:
      - "8080:8080"
    environment:
      DATABASE_URL: postgres://app:app@db:5432/app
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
      POSTGRES_DB: app
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  pgdata:
```

Service name `db` is the hostname from inside `api`. That's Compose DNS.

---

## Common footguns

| Symptom | Likely cause |
|---|---|
| Huge image | Dev tools left in final stage; no multi-stage |
| "Works in Compose, fails in K8s" | Hardcoded `localhost` instead of service name |
| Permission denied in container | Running as non-root but files owned by root |
| Build context huge / slow | Missing `.dockerignore` |
| Port already allocated | Something else on host port — change mapping |

---

*Part of [devops-to-ai](../../README.md) — Phase 01: Core DevOps*
