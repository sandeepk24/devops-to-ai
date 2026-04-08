# Project: Automated server health reporter

> Phase 00 capstone project — build this before moving to Phase 01.

A Python + Bash system that SSHes into multiple servers, collects health metrics, compares against thresholds, generates a report, and emails it on a schedule. No cloud services, no monitoring platforms — just the fundamentals.

---

## What you're building

```
config.yaml          ← define your servers and alert thresholds
reporter.py          ← main Python script (SSH, collect, analyse, report)
run.sh               ← Bash wrapper (called by cron)
reports/             ← generated reports land here (created automatically)
logs/                ← script logs land here (created automatically)
```

---

## Requirements

- Python 3.9+
- `paramiko` — SSH from Python (`pip install paramiko`)
- `pyyaml` — YAML parsing (`pip install pyyaml`)
- Access to at least one Linux server via SSH key (a free-tier cloud VM works)

---

## Setup

```bash
# Clone or copy this project
cd server-health-reporter

# Install dependencies
pip install -r requirements.txt

# Copy and edit the config
cp config.example.yaml config.yaml
# Edit config.yaml with your server IPs and SSH key path

# Test it runs
python reporter.py --config config.yaml

# Check the report was generated
ls reports/
```

---

## Configuration

Edit `config.yaml` — see `config.example.yaml` for the full format:

```yaml
settings:
  report_format: html          # html or text
  report_dir: ./reports
  log_file: ./logs/reporter.log
  email:
    enabled: false             # set to true and fill in details to enable email
    smtp_host: smtp.gmail.com
    smtp_port: 587
    username: your@email.com
    password: ""               # use env var: export SMTP_PASSWORD=...
    to: alerts@yourteam.com

thresholds:
  cpu_percent: 80
  disk_percent: 85
  memory_percent: 90

servers:
  - name: web-01
    host: 192.168.1.10
    user: ubuntu
    key_path: ~/.ssh/id_ed25519
  - name: db-01
    host: 192.168.1.11
    user: ubuntu
    key_path: ~/.ssh/id_ed25519
```

---

## Setting up the cron job

```bash
# Make the wrapper executable
chmod +x run.sh

# Open crontab
crontab -e

# Add this line to run every 6 hours:
0 */6 * * * /full/path/to/server-health-reporter/run.sh

# Verify it was added
crontab -l
```

---

## Your tasks

The `reporter.py` file has `TODO` comments marking everything you need to implement. Work through them in order — each one builds on the previous.

**Core tasks (required):**
- [ ] Connect to each server via SSH using paramiko
- [ ] Collect CPU usage, disk usage per partition, memory usage
- [ ] Collect top 5 CPU-consuming processes
- [ ] Collect last 10 lines of `/var/log/syslog`
- [ ] Compare metrics against thresholds from config
- [ ] Generate a formatted text or HTML report
- [ ] Handle unreachable servers gracefully — log and continue
- [ ] Save the report to the `reports/` directory with a timestamp in the filename

**Stretch goals (optional):**
- [ ] Send the report via email when thresholds are breached
- [ ] Add a `--dry-run` flag that shows what would happen without connecting
- [ ] Store previous reports and include a trend comparison (this week vs last week)
- [ ] Add a Slack webhook notification

---

## What a completed project looks like

When you're done, you should be able to:

1. Run `python reporter.py --config config.yaml` and see a report generated in `reports/`
2. Intentionally fill up disk on a test server and see a threshold breach flagged in the report
3. Point the config at an unreachable server and watch the script continue with the others
4. Show `crontab -l` and see the job scheduled
5. Show the `logs/` directory with timestamped log files

That's the definition of done. Not "it runs on my machine once" — it runs unattended, handles failure, and produces useful output.

---

## Sharing your work

When you complete this project, open a `[Phase 00] Done` issue on the [devops-to-ai repo](https://github.com/sandeepk24/devops-to-ai) and link your GitHub repo. Looking at someone else's completed capstone is one of the best ways to learn.
