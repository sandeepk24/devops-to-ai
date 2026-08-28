# Networking cheatsheet

**Use this when:** a service cannot connect, DNS looks wrong, or you need to verify a port is open.  
**Debug order:** DNS → port reachable → firewall → application logs.

---

## The 30-second mental model

```
Browser/curl
    → DNS (hostname → IP address)
    → TCP connect (IP + port)
    → TLS handshake (HTTPS only)
    → HTTP request/response
```

Common ports:

| Port | Service |
|---|---|
| 22 | SSH |
| 80 | HTTP |
| 443 | HTTPS |
| 3306 | MySQL |
| 5432 | PostgreSQL |
| 6379 | Redis |
| 8080 | Common app port |

---

## DNS

```bash
dig example.com                    # full lookup
dig example.com +short             # just the IP
dig example.com MX                 # mail records
nslookup example.com               # simpler lookup
host example.com                   # quick lookup
```

**If DNS fails:** check `/etc/resolv.conf`, try `dig @8.8.8.8 example.com` to rule out local resolver issues.

---

## Connectivity

```bash
ping -c 4 hostname                 # basic reachability (ICMP — may be blocked)
traceroute hostname                # path to host
curl -v https://example.com        # full HTTP + TLS details (most useful)
curl -I https://example.com        # headers only
curl -o /dev/null -s -w "%{http_code}\n" https://example.com   # status code only
```

---

## Ports & listeners

```bash
ss -tuln                           # listening TCP/UDP ports
ss -tulnp                          # + process name (needs sudo)
lsof -i :443                       # what's using port 443
nc -zv hostname 443                # is port open? (netcat)
nc -zv hostname 22-443             # scan a range
```

On the server itself:

```bash
curl localhost:8080/health          # app responding locally?
ss -tuln | grep 8080               # is the app listening?
```

---

## TLS / certificates

```bash
openssl s_client -connect example.com:443 -servername example.com </dev/null 2>/dev/null | openssl x509 -noout -dates -subject
# shows cert expiry and subject

curl -vI https://example.com 2>&1 | grep -E "subject|issuer|expire"
```

**Common TLS errors:**
- Certificate expired → renew cert (Let's Encrypt, cert-manager, etc.)
- Hostname mismatch → wrong cert on that IP
- Self-signed → expected in dev; use proper CA in prod

---

## Firewall (Linux)

```bash
# Ubuntu/Debian
sudo ufw status
sudo ufw allow 443/tcp

# RHEL/CentOS
sudo firewall-cmd --list-all
```

Also check **cloud security groups** — the #1 cause of "works locally, fails in prod."

---

## Troubleshooting flowchart

```
Can't reach service?
│
├─ dig hostname fails?        → DNS problem
├─ dig OK, nc/curl fails?     → firewall, security group, or service down
├─ curl localhost OK,
│  curl remote fails?          → firewall / wrong bind address (0.0.0.0 vs 127.0.0.1)
└─ HTTP 5xx but connection OK? → application problem (check logs)
```

---

## Useful one-liners

```bash
# Which DNS server am I using?
cat /etc/resolv.conf

# Show my IP addresses
ip addr show

# Show routing table
ip route

# Test DNS + HTTP in one go
curl -v --connect-timeout 5 https://api.example.com/health

# Watch connections in real time (needs sudo)
watch -n 1 'ss -s'
```

---

*Part of [devops-to-ai](../../README.md) — Phase 00: The Foundation*
