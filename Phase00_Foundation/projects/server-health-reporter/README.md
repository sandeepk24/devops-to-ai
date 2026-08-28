# Capstone: Server health reporter

> **Phase 00 project** — build this before [Phase 01](../../../Phase01_Core_DevOps/README.md).  
> Full phase guide: [Phase 00 README](../../README.md)

A Python + Bash tool that SSHes into servers, collects health metrics, compares them to thresholds, and saves a report. Scheduled with cron. No cloud, no fancy monitoring stack — just the fundamentals you will use every day as a DevOps engineer.

---

## What you are building

```
config.yaml     ← servers + thresholds
reporter.py     ← SSH, collect metrics, write report
run.sh          ← Bash wrapper for cron
reports/        ← output (auto-created)
logs/           ← logs (auto-created)
```

**Skills this proves:** SSH automation, remote command execution, config-driven tools, error handling, cron scheduling.

---

## Before you start

You need:

- **Python 3.9+**
- **One Linux server** you can SSH into (free cloud VM is fine)
- **SSH key auth** set up (`ssh-copy-id user@your-server`)

```bash
# Quick test — should connect without a password prompt
ssh -i ~/.ssh/id_ed25519 user@YOUR_SERVER_IP "uptime"
```

---

## Setup (5 minutes)

```bash
cd Phase00_Foundation/projects/server-health-reporter

# 1. Install dependencies
pip install -r requirements.txt

# 2. Create your config
cp config.example.yaml config.yaml
# Edit config.yaml — set your server IP, user, and key path

# 3. Dry run (lists servers, no SSH yet — implement --dry-run in reporter.py first)
python reporter.py --config config.yaml --dry-run

# 4. Run for real
python reporter.py --config config.yaml

# 5. Check output
ls reports/
cat logs/reporter.log
```

---

## Config example

```yaml
settings:
  report_format: html          # html or text
  report_dir: ./reports
  log_file: ./logs/reporter.log
  email:
    enabled: false             # stretch goal — see reporter.py

thresholds:
  cpu_percent: 80
  disk_percent: 85
  memory_percent: 90

servers:
  - name: web-01
    host: 203.0.113.10         # your VM IP
    user: ubuntu
    key_path: ~/.ssh/id_ed25519
```

See [config.example.yaml](./config.example.yaml) for the full template.

---

## What to implement

Open `reporter.py` and work through the **TODO** comments in order:

| Step | Function | What it does |
|---|---|---|
| 1 | `load_config()` | Validate required YAML fields |
| 2 | `connect_ssh()` | Connect with paramiko; return `None` on failure |
| 3 | `collect_metrics()` | Run remote commands for CPU, memory, disk, processes, logs |
| 4 | `check_thresholds()` | Return list of alert strings |
| 5 | `generate_report()` | Build text or HTML report |
| 6 | `main()` | Wire it all together; skip failed servers |

**Remote commands** (hints are in `reporter.py`):

```bash
# CPU
top -bn1 | grep "Cpu(s)"

# Memory
free | awk '/^Mem:/ {printf "%.1f", $3/$2 * 100}'

# Disk
df -h

# Top processes
ps aux --sort=-%cpu | head -6

# Recent logs
tail -n 10 /var/log/syslog
```

---

## Schedule with cron

```bash
chmod +x run.sh
crontab -e

# Run every 6 hours — use the FULL path to run.sh
0 */6 * * * /full/path/to/server-health-reporter/run.sh

crontab -l    # verify
```

---

## Definition of done

- [ ] `python reporter.py --config config.yaml` creates a timestamped report in `reports/`
- [ ] CPU / memory / disk shown for each reachable server
- [ ] Bad server in config → logged as unreachable, others still checked
- [ ] Threshold breach clearly marked in report (try filling disk on a test VM)
- [ ] Cron entry exists and `logs/` has entries from scheduled runs

**Stretch goals (optional):**
- Email report when thresholds breached
- `--dry-run` flag
- Slack webhook notification

---

## When you finish

Open a `[Phase 00] Done` issue on the [devops-to-ai repo](https://github.com/sandeepk24/devops-to-ai) and link your GitHub repo.

Then move to → [Phase 01 — Core DevOps](../../../Phase01_Core_DevOps/README.md)
