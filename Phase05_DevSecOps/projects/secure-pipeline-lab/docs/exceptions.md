# Temporary scan exceptions — Phase 05 lab
#
# Use this only when you must ship with a known finding.
# Infinite ignores with no owner are how vulns become "normal."

| CVE / finding | Why waived | Compensating control | Owner | Expiry (YYYY-MM-DD) | Ticket |
|---|---|---|---|---|---|
| _(example)_ CVE-2099-0001 | No fixed package yet in debian slim | Network policy + WAF; not internet-facing | you@example.com | 2099-01-31 | INC-123 |

## Rules of thumb

1. Prefer upgrading the package or base image.
2. If you waive: fill every column above; delete the row when fixed.
3. Mirror the same IDs in `.trivyignore` only while the row is active.
4. Re-scan on expiry — waived ≠ forever green.
