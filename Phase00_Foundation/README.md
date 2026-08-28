# Phase 00 — The Foundation

> **"You cannot automate what you don't understand manually."**
>
> Before Docker, Kubernetes, or CI/CD — you need the basics: Linux, scripts, Git, and how servers talk to each other. This phase builds that base. Everything in Phase 01+ assumes you are comfortable here.

---

## Who this is for

| You are... | Do this |
|---|---|
| New to Linux / servers | Work through every topic, then the capstone |
| Junior DevOps, rusty on fundamentals | Skim topics, use cheatsheets, build the capstone |
| Experienced Linux admin | Take the [self-check](#self-check--can-you-skip) below — if you pass, jump to Phase 01 |

**Time:** 4–6 weeks part-time  
**Goal:** Operate a Linux server from the terminal and automate a small real task without a GUI.

---

## Start here — four steps

```
1. Self-check     →  Already know this stuff? Skip to Phase 01
2. Learn          →  Work through the 7 topics below (use cheatsheets)
3. Practice       →  Run commands on a real Linux VM (free cloud tier is fine)
4. Capstone       →  Build the server health reporter (required before Phase 01)
```

**Get a practice server:** Any Linux VM with SSH access works — AWS free tier, GCP, DigitalOcean, or a local VM.

**Cheatsheets in this repo (bookmark these):**

| Topic | Cheatsheet |
|---|---|
| Linux commands | [cheatsheets/linux-commands.md](./cheatsheets/linux-commands.md) |
| Bash scripting | [cheatsheets/bash-patterns.md](./cheatsheets/bash-patterns.md) |
| Git | [cheatsheets/git-commands.md](./cheatsheets/git-commands.md) |
| Networking | [cheatsheets/networking.md](./cheatsheets/networking.md) |

---

## Self-check — can you skip?

If you can do **all** of these without looking things up, skip to [Phase 01](../Phase01_Core_DevOps/README.md):

- SSH into a server with a key and run `systemctl`, `journalctl`, and `df -h`
- Write a Bash script with `set -euo pipefail`, a function, and error handling
- Explain DNS → TCP → TLS → HTTP when you `curl https://example.com`
- Write a short Python script that reads YAML and calls a REST API
- Rebase a feature branch onto `main` and resolve a merge conflict
- Use `grep`, `awk`, and `sed` on a log file to find errors

Otherwise, stay here and fill the gaps.

---

## Learning objectives

By the end of Phase 00, you should answer **yes** to all of these:

- [ ] Navigate and manage files on Linux from the terminal only
- [ ] Write a Bash script that handles errors and can run from cron
- [ ] Diagnose a connectivity problem with `ping`, `dig`, `curl`, and `ss`
- [ ] Write Python that reads config files, calls APIs, and handles failures
- [ ] Use Git branches, rebase, and revert — not just `add` / `commit` / `push`
- [ ] Explain SSH keys and why TLS matters for HTTPS
- [ ] Read and write YAML and JSON (you will use these every day in DevOps)

---

## Topics

Each section is **practical** — focused on what you use in real infrastructure work.

### 1. Linux & the terminal

**Why DevOps needs this:** Every server, container, and CI job runs on Linux. You will live in the terminal.

**Learn:**
- Where things live: `/etc` (config), `/var/log` (logs), `/tmp` (temp), `/home` (users)
- Permissions: `chmod`, `chown`, `ls -la`
- Processes & services: `ps`, `top`, `systemctl`, `journalctl`
- Logs: `tail -f`, `grep`, `less`
- Packages: `apt install` / `dnf install`
- Disk & memory: `df -h`, `free -h`, `du -sh`

**Practice:** SSH into a VM. Find the largest log file, check disk usage, restart a service, read its logs.

→ [Linux cheatsheet](./cheatsheets/linux-commands.md)

---

### 2. Bash scripting

**Why DevOps needs this:** Cron jobs, CI steps, deploy scripts, health checks — most glue code is Bash.

**Learn:**
- Start every script with: `set -euo pipefail`
- Variables, `if`/`for`, functions
- Exit codes, `trap`, and logging
- Arguments with `getopts`
- Safe patterns: retries, lock files, `mktemp`

**Rule:** A script is not done until it fails loudly and leaves useful logs.

→ [Bash cheatsheet](./cheatsheets/bash-patterns.md) · [ShellCheck](https://www.shellcheck.net/)

---

### 3. Networking basics

**Why DevOps needs this:** "The app can't reach the database" is a daily problem. You need a simple mental model.

**Learn:**
- IP + ports (22=SSH, 80=HTTP, 443=HTTPS)
- DNS: what `dig` and `nslookup` show you
- TCP vs UDP (most apps use TCP)
- HTTP: methods, status codes, headers
- Debug toolkit: `ping`, `traceroute`, `dig`, `curl -v`, `ss -tuln`

**Simple debug order when something won't connect:**

```
DNS resolves?  →  port open?  →  firewall/security group?  →  app listening?
     dig            nc / ss           ufw / cloud rules         curl / logs
```

→ [Networking cheatsheet](./cheatsheets/networking.md)

---

### 4. Python for automation

**Why DevOps needs this:** Python glues APIs, parses logs, reads config, and powers tools you will build later.

**Learn:**
- Files, JSON, YAML (`json`, `pyyaml`)
- HTTP requests (`requests` or `httpx`)
- `try`/`except`, environment variables, `argparse`
- Running commands: `subprocess`
- Virtual envs: `python -m venv .venv`

**Skip for now:** web frameworks, data science, async.

**Resource:** [Automate the Boring Stuff](https://automatetheboringstuff.com/) — chapters 1–11

---

### 5. Git

**Why DevOps needs this:** Pipelines, infra repos, and rollbacks all run on Git. Surface-level Git is not enough.

**Learn:**
- Commits are snapshots; staging vs working directory
- Branches, merge, rebase (and when **not** to rebase shared branches)
- `git revert` vs `git reset`
- `git reflog` — undo mistakes
- Conventional commits: `feat:`, `fix:`, `chore:`

→ [Git cheatsheet](./cheatsheets/git-commands.md) · [Learn Git Branching](https://learngitbranching.js.org/)

---

### 6. YAML, JSON & jq

**Why DevOps needs this:** Kubernetes, GitHub Actions, Terraform, and Ansible are mostly YAML and JSON.

**Learn:**
- YAML indentation rules (spaces, not tabs)
- JSON structure for API responses
- `jq` for querying JSON on the command line
- Basic regex for log parsing (`grep -E`)

**Tools:** [jq play](https://jqplay.org/) · [regex101](https://regex101.com/)

---

### 7. SSH & TLS

**Why DevOps needs this:** You access every server over SSH. Every HTTPS call depends on TLS.

**Learn:**
- Generate keys: `ssh-keygen -t ed25519`
- Copy key: `ssh-copy-id user@host`
- `~/.ssh/config` for shortcuts
- TLS in one sentence: server proves identity with a certificate; traffic is encrypted
- Inspect certs: `openssl s_client -connect host:443`

---

## Capstone project

Build a **server health reporter** — a small Python + Bash system that:

1. Reads server list + alert thresholds from YAML
2. SSHes into each server and collects CPU, memory, disk, top processes, recent logs
3. Flags anything over threshold
4. Writes a report to disk
5. Runs on a schedule via cron
6. Keeps going when one server is down

This is intentionally boring infrastructure — no cloud dashboards, no Kubernetes. That is the point.

**Starter code and full instructions:**

→ [projects/server-health-reporter/README.md](./projects/server-health-reporter/README.md)

**Definition of done:**
- [ ] Report generates when you run `python reporter.py --config config.yaml`
- [ ] Unreachable server is logged; other servers still checked
- [ ] Threshold breach shows clearly in the report
- [ ] Cron job is scheduled (`crontab -l` shows it)
- [ ] Logs written to `logs/`

---

## Ready for Phase 01?

Do not move on until you can do these **without googling**:

1. Write a Bash script with functions and `set -euo pipefail`
2. SSH to a server with a key you created
3. Explain what happens when you run `curl -v https://google.com` (DNS → connect → TLS → HTTP)
4. Write Python that reads YAML and handles a failed API call
5. Squash your last 3 commits with `git rebase -i`
6. Pull errors from a log with `grep` and `awk`

Stuck on any of these? Spend more time here — Phase 01 moves fast.

---

## Resources

| Resource | What it's for |
|---|---|
| [The Linux Command Line](https://linuxcommand.org/tlcl.php) | Deep Linux reference (free) |
| [OverTheWire: Bandit](https://overthewire.org/wargames/bandit/) | Learn Linux by doing puzzles |
| [Pro Git](https://git-scm.com/book/en/v2) | Git reference (free) |
| [Automate the Boring Stuff](https://automatetheboringstuff.com/) | Python automation (free) |
| [ShellCheck](https://www.shellcheck.net/) | Lint your Bash scripts |
| Repo cheatsheets | Day-to-day command reference |

---

## Track your progress

Open a GitHub issue: `[Phase 00] Starting` when you begin, `[Phase 00] Done` when the capstone works. Link your repo in the Done issue.

---

*Next: [Phase 01 — Core DevOps →](../Phase01_Core_DevOps/README.md)*
