# Phase 00 — The Foundation

> **"You cannot automate what you don't understand manually."**
>
> Every senior engineer you admire has this phase burned into muscle memory. Skip it and you'll spend the next five years googling things that should be instinct. Do it properly and every phase after this gets dramatically easier.

---

## What this phase is

This is not a DevOps phase. It is not a cloud phase. It is the phase where you become dangerous with a terminal, fluent with a script, and comfortable in the infrastructure that everything else runs on. Junior engineers who rush past this are the ones who can follow a tutorial but can't debug when it breaks.

By the end of Phase 00 you should be able to sit at a blank Linux server with no GUI, no hints, and no stack overflow — and get things done.

**Estimated time:** 4–6 weeks  
**Target audience:** Complete beginners, career switchers, CS graduates who've never touched a real server  
**Skippable if:** You've administered Linux servers professionally and can write Python scripts from memory

---

## Learning objectives

When you finish this phase, you should be able to answer yes to all of these:

- [ ] Can you navigate, search, and manipulate a Linux filesystem entirely from the command line?
- [ ] Can you read and write a Bash script that uses conditionals, loops, functions, and handles errors gracefully?
- [ ] Can you explain what happens at the network layer when you type a URL into a browser?
- [ ] Can you write a Python script that reads files, calls an API, parses JSON, and handles exceptions?
- [ ] Can you use Git beyond just `add`, `commit`, `push` — do you understand rebasing, cherry-picking, and resolving conflicts?
- [ ] Do you understand how TLS works and why it matters?
- [ ] Can you parse and write YAML and JSON without looking up the syntax?

If you can say yes to all seven, you're ready for Phase 01.

---

## Topics

### 1. Linux & shell mastery

This is the single most leveraged skill in infrastructure engineering. Everything runs on Linux. Learn it like a native speaker, not a tourist.

**What to cover:**
- Filesystem hierarchy — where things live and why (`/etc`, `/var`, `/proc`, `/sys`, `/tmp`)
- File permissions and ownership (`chmod`, `chown`, `umask`, `ACLs`)
- Process management (`ps`, `top`, `htop`, `kill`, `nice`, `systemctl`, `journalctl`)
- Package management (`apt`, `yum`/`dnf`, building from source)
- Text processing — the real power: `grep`, `awk`, `sed`, `cut`, `sort`, `uniq`, `wc`, `tr`
- Input/output redirection and pipes — the Unix philosophy in practice
- Cron jobs and scheduled tasks
- Environment variables and the shell profile (`~/.bashrc`, `~/.profile`, `PATH`)
- `ssh`, `scp`, `rsync` — moving around and moving files
- `curl` and `wget` — talking to the internet from the terminal
- `strace`, `lsof`, `netstat`/`ss` — debugging when nothing else works

**Recommended resources:**
- [The Linux Command Line](https://linuxcommand.org/tlcl.php) by William Shotts — free, comprehensive, the best book on this
- [OverTheWire: Bandit](https://overthewire.org/wargames/bandit/) — learn Linux by hacking your way through puzzles (genuinely the most effective method)
- [explainshell.com](https://explainshell.com) — paste any command and understand every flag

---

### 2. Bash scripting

Bash is the glue that holds infrastructure together. You'll write it constantly — for CI steps, cron jobs, deployment hooks, health checks, and automation tasks. The goal isn't to become a Bash wizard; it's to be able to write a reliable script without having to think too hard about the syntax.

**What to cover:**
- Variables, arrays, and string manipulation
- Conditionals (`if`/`elif`/`else`, `case`)
- Loops (`for`, `while`, `until`)
- Functions — parameters, return values, scope
- Exit codes and error handling (`set -e`, `set -o pipefail`, `trap`)
- Reading input, parsing arguments (`getopts`)
- Heredocs
- Writing scripts that are safe to re-run (idempotency)

**A script is not finished until it handles failure gracefully.** Every script you write in this phase should have error handling. Get into that habit now.

**Recommended resource:**
- [Bash scripting cheatsheet](https://devhints.io/bash) — keep this open while writing scripts
- [ShellCheck](https://www.shellcheck.net/) — paste your script, get instant feedback. Use it for every script you write.

---

### 3. Networking fundamentals

This is the topic most junior engineers skip and then spend years being confused by. You don't need to pass a CCNA exam — you need a working mental model of how data moves.

**What to cover:**
- The OSI model — not to memorise layers, but to understand why it exists
- IP addressing, subnets, CIDR notation — you should be able to calculate this without a tool
- DNS — how resolution works, what a record is, A vs CNAME vs MX vs TXT, TTL
- TCP vs UDP — when and why each is used
- HTTP/S — request/response cycle, headers, methods, status codes, TLS handshake
- Ports and what's running on them — why 80, 443, 22, 3306 matter
- Firewalls and network security groups at a conceptual level
- `ping`, `traceroute`, `dig`, `nslookup`, `curl -v`, `tcpdump` — the diagnostic toolkit
- NAT, private vs public IP addresses, how your home router works

**The test:** If someone tells you "my app can't reach the database," you should be able to systematically diagnose whether it's a DNS problem, a firewall problem, a routing problem, or an application problem — using only terminal tools.

**Recommended resource:**
- [Julia Evans' networking zines](https://jvns.ca/networking-zine.pdf) — the most approachable introduction to networking that exists
- [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/) — optional, but excellent if you want depth

---

### 4. Python for automation

Python is the automation language of infrastructure. You'll use it to write tools, glue APIs together, process data, and eventually build AI integrations in later phases. Learn it with an infrastructure mindset — not as a web developer or data scientist would.

**What to cover:**
- Data types, control flow, functions, classes — the basics, done properly
- File I/O — reading, writing, appending, using `pathlib`
- Working with JSON, YAML (`json`, `pyyaml` libraries)
- Making HTTP requests (`requests` library, handling responses, errors, retries)
- Error handling — `try`/`except`/`finally`, raising exceptions, custom exceptions
- Working with environment variables (`os.environ`)
- Running shell commands from Python (`subprocess`)
- Writing command-line tools with `argparse`
- Virtual environments and `pip` — how Python packaging works
- Basic object-oriented programming — enough to read and write classes

**What to skip for now:** Web frameworks, async/await, data science libraries. Those come later.

**Recommended resources:**
- [Automate the Boring Stuff with Python](https://automatetheboringstuff.com/) — free online, chapters 1–11 are directly applicable
- [Python for DevOps](https://www.oreilly.com/library/view/python-for-devops/9781492057680/) — O'Reilly book specifically for infrastructure use cases

---

### 5. Git internals & workflows

Most engineers use Git at the surface level. You'll be working with it every day for the rest of your career, and there's no excuse not to understand what's actually happening under the hood.

**What to cover:**
- What a commit actually is — a snapshot, not a diff
- The three trees: working directory, staging area (index), repository
- Branching and merging — fast-forward vs three-way merge, and when each happens
- Rebasing — interactive rebase, squashing, rewriting history, and why you should never rebase shared branches
- `git reflog` — your safety net
- Cherry-picking
- Tags — lightweight vs annotated, why they're used for releases
- `.gitignore` patterns
- Resolving merge conflicts properly — not just clicking "accept theirs"
- Git hooks — pre-commit, pre-push, and how to use them
- A real branching strategy: trunk-based development vs GitFlow, and the tradeoffs

**Recommended resource:**
- [Pro Git](https://git-scm.com/book/en/v2) — free, authoritative, chapters 1–3 and 7 are essential
- [Learn Git Branching](https://learngitbranching.js.org/) — interactive visual exercises, extremely effective

---

### 6. YAML, JSON & the data formats of infrastructure

You will read and write YAML constantly — Kubernetes manifests, CI/CD pipeline definitions, Ansible playbooks, Helm values files. JSON is everywhere in APIs and config. Regex comes up more than you'd like. Get fluent.

**What to cover:**
- YAML syntax — scalars, sequences, mappings, anchors (`&`) and aliases (`*`), multi-line strings
- Common YAML gotchas — indentation, yes/no being parsed as booleans, tabs vs spaces
- JSON — structure, parsing, nested objects, arrays
- `jq` — the command-line JSON processor. This one tool will save you hours
- Basic regex — character classes, quantifiers, anchors, groups, lookaheads
- Using regex in `grep -E`, `sed`, and Python's `re` module

**Recommended resource:**
- [jq play](https://jqplay.org/) — interactive jq testing, use it while learning
- [regex101.com](https://regex101.com/) — write and test regex with real-time explanation

---

### 7. SSH & TLS — how credentials and encryption work

You'll use SSH every day and TLS is the foundation of secure communication everywhere. Understand them, don't just use them.

**What to cover:**
- How SSH key pairs work — public vs private key, the authentication flow
- Generating keys (`ssh-keygen`), managing `~/.ssh/config`, SSH agent forwarding
- `ssh-copy-id`, authorized_keys, known_hosts
- How TLS works — certificates, the handshake, certificate chains, root CAs
- Self-signed certificates vs CA-signed — why it matters
- `openssl` commands for inspecting and generating certificates

---

## Capstone project

### Automated server health reporter

**Build a system that does exactly this:**

1. Reads a list of server IPs from a YAML config file
2. SSHes into each server using Python's `paramiko` library (or Bash with `ssh`)
3. Collects: CPU usage, available disk space per partition, memory usage, top 5 CPU-consuming processes, last 10 lines of `/var/log/syslog`
4. Compares metrics against thresholds defined in the YAML config
5. Generates a formatted report — either as a text file or a simple HTML file
6. Sends the report via email using Python's `smtplib` or a free service like Mailgun
7. Is scheduled via a cron job to run every 6 hours
8. Handles failures gracefully — if a server is unreachable, log the error and continue with the others

**No cloud services. No monitoring platforms. No external dashboards.** Just Python, Bash, SSH, and the Linux tools you've learned. The constraint is the point.

**What you'll learn from building this that you can't learn from tutorials:**
- Writing Python that handles real network failures
- Parsing and validating config files defensively
- Structuring a project with multiple files and a proper `README`
- Writing a Bash wrapper that can be dropped into cron
- The satisfaction of something running unattended and working

**Stretch goals:**
- Add a `--dry-run` flag that shows what would happen without doing anything
- Store historical reports and generate a simple trend comparison
- Add Slack webhook notifications alongside the email

---

## How to know you're ready for Phase 01

Do not move on until you can do all of the following without googling:

- Write a Bash script with functions, error handling, and `set -e`/`set -o pipefail`
- Explain the difference between a hard link and a symbolic link
- Set up SSH key authentication to a remote server from scratch
- Explain what happens — step by step, at the network layer — when you run `curl https://google.com`
- Write a Python script that reads a YAML file, calls a REST API, and writes the response to a JSON file
- Use `git rebase -i` to squash the last 3 commits into one
- Use `grep`, `awk`, and `sed` to extract and transform data from a log file

If any of those trips you up, go back and spend more time. Phase 01 assumes this is solid.

---

## Resources summary

| Resource | Type | Cost | Link |
|---|---|---|---|
| The Linux Command Line | Book | Free | [linuxcommand.org](https://linuxcommand.org/tlcl.php) |
| OverTheWire: Bandit | Interactive | Free | [overthewire.org](https://overthewire.org/wargames/bandit/) |
| Pro Git | Book | Free | [git-scm.com](https://git-scm.com/book/en/v2) |
| Learn Git Branching | Interactive | Free | [learngitbranching.js.org](https://learngitbranching.js.org/) |
| Automate the Boring Stuff | Book | Free | [automatetheboringstuff.com](https://automatetheboringstuff.com/) |
| Julia Evans networking zine | Zine | Free | [jvns.ca](https://jvns.ca/networking-zine.pdf) |
| ShellCheck | Tool | Free | [shellcheck.net](https://www.shellcheck.net/) |
| jq play | Tool | Free | [jqplay.org](https://jqplay.org/) |
| regex101 | Tool | Free | [regex101.com](https://regex101.com/) |

---

## Community & tracking

If you're working through this roadmap, open an issue with the title `[Phase 00] Starting` when you begin and `[Phase 00] Done` when you complete the capstone project. This keeps you accountable and helps others who are at the same stage find each other.

---

*Next: [Phase 01 — Core DevOps →](../Phase01_Core_DevOps/README.md)*
