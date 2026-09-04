# Scanning cheatsheet (SCA & images)

**Use this when:** you're wiring CI gates or debugging "why did Trivy fail my PR?"  
**Rule of thumb:** fail on HIGH/CRITICAL first. Failing on every LOW trains people to skip the job.

---

## Three different scans

| Kind | Question it answers | Typical tool |
|---|---|---|
| SCA (deps) | Are my library versions known-bad? | `pip-audit`, npm audit, Trivy fs |
| Image | What's broken *inside the built image*? | Trivy image, Grype |
| FS / IaC | Any secrets or misconfig in the repo? | Trivy fs/config, Checkov |

Scan the **image you ship**, not only the Dockerfile. Multi-stage builds can hide OS packages in the final stage.

---

## Trivy without installing it

```bash
# Filesystem / repo (deps + misconfig)
docker run --rm -v "$PWD:/src" aquasec/trivy:0.58.1 fs \
  --severity HIGH,CRITICAL --exit-code 1 /src

# Built image
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:0.58.1 image --severity HIGH,CRITICAL --exit-code 1 IMAGE:TAG
```

`--exit-code 1` = fail the script/CI when findings match the severity filter.

---

## Python SCA quick check

```bash
python -m pip install pip-audit
pip-audit -r requirements.txt
```

If CI has no network to a vuln DB, prefer the Trivy image (it bundles DBs) or cache the DB in Actions.

---

## Reading a finding

Ask, in order:

1. Is there a fixed version? Upgrade.
2. Is the vulnerable code path actually reachable? Still track it — don't hand-wave.
3. Need time? Exception with owner + expiry (see Phase 05 guide) — not a silent ignore forever.

---

## Common footguns

- Scanning `python:latest` locally but shipping a different digest in prod
- Ignoring `.trivyignore` growth with no tickets
- Only scanning `main` — vulns land on feature branches too
- Treating "0 vulnerabilities" as "secure" (logic bugs, bad IAM, and secrets still exist)

---

## Useful links

- [Trivy](https://aquasecurity.github.io/trivy/)
- [pip-audit](https://pypi.org/project/pip-audit/)
- Phase 05 lab: `projects/secure-pipeline-lab/scripts/scan_local.sh`
