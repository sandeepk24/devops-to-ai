#!/usr/bin/env python3
"""
Automated server health reporter — Phase 00 capstone project.

Usage:
    python reporter.py --config config.yaml
    python reporter.py --config config.yaml --dry-run
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import yaml

# TODO: import paramiko for SSH connections
# TODO: import smtplib and email.mime modules if implementing email


# ── logging setup ──────────────────────────────────────────────────────────────

def setup_logging(log_file: str) -> logging.Logger:
    """Set up logging to both console and file."""
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("reporter")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# ── config loading ─────────────────────────────────────────────────────────────

def load_config(config_path: str) -> dict:
    """Load and validate configuration from YAML file."""
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"config file not found: {config_path}")

    if not path.is_file():
        raise ValueError(f"config path is not a file: {config_path}")

    with open(path) as f:
        config = yaml.safe_load(f)

    # TODO: validate required fields exist in config
    # Hint: check that config has 'servers', 'thresholds', 'settings'
    # Raise a ValueError with a helpful message if anything is missing

    return config


# ── ssh connection ─────────────────────────────────────────────────────────────

def connect_ssh(host: str, user: str, key_path: str):
    """
    Create an SSH connection to a server.

    Returns a connected paramiko SSHClient, or None if connection fails.
    Should never raise an exception — log the error and return None.
    """
    # TODO: implement this function
    # Hints:
    #   - Use paramiko.SSHClient()
    #   - Set missing host key policy: client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #   - Connect with: client.connect(hostname=host, username=user, key_filename=key_path)
    #   - Wrap in try/except and return None if connection fails
    #   - Expand ~ in key_path: os.path.expanduser(key_path)
    pass


# ── metric collection ──────────────────────────────────────────────────────────

def collect_metrics(ssh_client) -> dict:
    """
    Collect health metrics from a connected server.

    Returns a dict with keys:
        cpu_percent      float
        memory_percent   float
        disks            list of {mount, used_percent, used_gb, total_gb}
        top_processes    list of {pid, cpu, mem, command} (top 5 by CPU)
        syslog_tail      list of str (last 10 lines)
    """
    # TODO: implement this function
    # Hints:
    # - Run commands with: stdin, stdout, stderr = ssh_client.exec_command("command")
    # - Read output with: output = stdout.read().decode().strip()
    #
    # Useful commands to run on the remote server:
    #   CPU usage:
    #     top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1
    #
    #   Memory usage:
    #     free | awk '/^Mem:/ {printf "%.1f", $3/$2 * 100}'
    #
    #   Disk usage:
    #     df -h | awk 'NR>1 {print $6, $5, $3, $2}'
    #
    #   Top 5 processes by CPU:
    #     ps aux --sort=-%cpu | head -6 | tail -5 | awk '{print $1, $2, $3, $4, $11}'
    #
    #   Last 10 lines of syslog:
    #     sudo tail -n 10 /var/log/syslog 2>/dev/null || tail -n 10 /var/log/messages 2>/dev/null
    pass


# ── threshold checking ─────────────────────────────────────────────────────────

def check_thresholds(metrics: dict, thresholds: dict) -> list:
    """
    Compare metrics against thresholds.

    Returns a list of alert strings for any metric that exceeds its threshold.
    Returns an empty list if everything is within limits.
    """
    # TODO: implement this function
    # Hints:
    # - Check cpu_percent against thresholds['cpu_percent']
    # - Check memory_percent against thresholds['memory_percent']
    # - Check each disk's used_percent against thresholds['disk_percent']
    # - Return a list like: ["CPU at 92% (threshold: 80%)", "Disk /var at 91% (threshold: 85%)"]
    pass


# ── report generation ──────────────────────────────────────────────────────────

def generate_report(results: list, report_format: str) -> str:
    """
    Generate a report from collected results.

    Args:
        results: list of dicts, one per server:
                 {name, host, status, metrics, alerts, error}
        report_format: 'html' or 'text'

    Returns the report as a string.
    """
    # TODO: implement this function
    # For 'text' format:
    #   Simple readable output with sections per server
    #   Mark ALERT clearly for any threshold breach
    #
    # For 'html' format:
    #   A simple but readable HTML page
    #   Use colour to highlight alerts (red) vs healthy (green)
    #   No external CSS frameworks — inline styles only
    pass


def save_report(content: str, report_dir: str, report_format: str) -> str:
    """Save report to file. Returns the file path."""
    output_dir = Path(report_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    extension = "html" if report_format == "html" else "txt"
    filename = f"health-report_{timestamp}.{extension}"
    filepath = output_dir / filename

    filepath.write_text(content)
    return str(filepath)


# ── email ──────────────────────────────────────────────────────────────────────

def send_email(config: dict, report_content: str, alerts: list, logger: logging.Logger):
    """
    Send the report via email. Only sends if there are alerts or email always_send is true.

    TODO (stretch goal): implement this function
    Hints:
    - Use smtplib.SMTP with STARTTLS
    - Get password from environment variable, not config file:
        password = os.environ.get('SMTP_PASSWORD', config['password'])
    - Subject line should include server count and alert count
    - Attach HTML report as the email body
    """
    pass


# ── main ───────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="collect health metrics from multiple servers and generate a report"
    )
    parser.add_argument("--config", required=True, help="path to config.yaml")
    parser.add_argument("--dry-run", action="store_true",
                        help="show what would happen without connecting to servers")
    return parser.parse_args()


def main():
    args = parse_args()

    config = load_config(args.config)
    logger = setup_logging(config["settings"]["log_file"])

    logger.info("server health reporter starting")
    logger.info(f"loaded config: {len(config['servers'])} servers configured")

    if args.dry_run:
        logger.info("DRY RUN — would connect to:")
        for server in config["servers"]:
            logger.info(f"  {server['name']} ({server['host']}) as {server['user']}")
        logger.info("no connections made")
        return

    results = []

    for server in config["servers"]:
        logger.info(f"connecting to {server['name']} ({server['host']})")

        result = {
            "name": server["name"],
            "host": server["host"],
            "status": "unknown",
            "metrics": None,
            "alerts": [],
            "error": None,
        }

        # TODO: connect to server using connect_ssh()
        # TODO: if connection fails, set result['status'] = 'unreachable', set result['error'], append to results and continue
        # TODO: collect metrics using collect_metrics()
        # TODO: check thresholds using check_thresholds()
        # TODO: set result['status'] to 'alert' if alerts, else 'healthy'
        # TODO: close the SSH connection

        results.append(result)

    # TODO: generate the report using generate_report()
    # TODO: save the report using save_report()
    # TODO: log how many servers were healthy vs alerts vs unreachable
    # TODO: if email is enabled in config, call send_email()

    logger.info("reporter finished")


if __name__ == "__main__":
    main()
