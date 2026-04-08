# Linux commands cheatsheet

Quick reference for the commands you'll use every day. Not exhaustive — focused on what actually matters in infrastructure work.

---

## Navigation & filesystem

```bash
pwd                          # where am I?
ls -la                       # list everything including hidden, with permissions
ls -lhS                      # sort by size, human readable
cd -                         # go back to previous directory
tree -L 2                    # directory tree 2 levels deep (install: apt install tree)

find / -name "*.log" 2>/dev/null          # find files by name, suppress errors
find /var -mtime -1 -type f               # files modified in the last 24 hours
find . -size +100M                        # files larger than 100MB
find . -type f -exec chmod 644 {} \;      # find and change permissions on all files

locate nginx.conf            # fast search using index (run updatedb first)
which python3                # show full path of a command
whereis nginx                # show binary, source, and man page locations
```

---

## File operations

```bash
cp -r source/ dest/          # copy directory recursively
cp -p file dest/             # copy preserving permissions and timestamps
mv file.txt ../              # move file up one directory
rm -rf dirname/              # delete directory and contents (no undo — be careful)

ln -s /etc/nginx/nginx.conf ~/nginx.conf    # create symlink
ln /etc/hosts /tmp/hosts-backup             # create hard link

cat file.txt                 # print file contents
less file.txt                # page through file (q to quit, / to search)
head -n 20 file.txt          # first 20 lines
tail -n 20 file.txt          # last 20 lines
tail -f /var/log/syslog      # follow a log file in real time
tail -f /var/log/syslog | grep ERROR   # follow and filter

wc -l file.txt               # count lines
wc -w file.txt               # count words
du -sh /var/log/             # size of a directory, human readable
du -sh /* 2>/dev/null | sort -rh | head   # find largest top-level directories
df -h                        # disk space on all mounted filesystems
```

---

## Permissions

```bash
# Format: [type][owner][group][other]
# Example: -rwxr-xr-- = file, owner rwx, group r-x, other r--

chmod 755 script.sh          # rwxr-xr-x  — owner full, others read+execute
chmod 644 config.txt         # rw-r--r--  — owner read+write, others read only
chmod 600 ~/.ssh/id_ed25519  # rw-------  — owner only (required for SSH keys)
chmod +x script.sh           # add execute for all
chmod -R 755 /var/www/       # recursive

chown user:group file.txt    # change owner and group
chown -R www-data:www-data /var/www/html/

# Numeric quick reference
# 4 = read, 2 = write, 1 = execute
# 7 = rwx, 6 = rw-, 5 = r-x, 4 = r--

umask 022                    # default: new files get 644, dirs get 755
```

---

## Text processing

```bash
# grep
grep "error" app.log                    # basic search
grep -i "error" app.log                 # case insensitive
grep -r "TODO" ./src/                   # recursive search in directory
grep -n "error" app.log                 # show line numbers
grep -v "DEBUG" app.log                 # invert — show lines NOT matching
grep -E "error|warn|fatal" app.log      # extended regex — match any of these
grep -A 3 -B 3 "FATAL" app.log         # show 3 lines after and before match
grep -c "error" app.log                 # count matching lines

# awk — column extraction and processing
awk '{print $1}' file.txt               # print first column
awk '{print $1, $3}' file.txt           # print columns 1 and 3
awk -F: '{print $1}' /etc/passwd        # use : as delimiter, print first column
awk '$3 > 1000' /etc/passwd             # print lines where column 3 > 1000
awk '{sum += $1} END {print sum}' file  # sum a column
awk 'NR==5,NR==10' file.txt             # print lines 5 to 10

# sed — stream editor
sed 's/old/new/' file.txt               # replace first occurrence per line
sed 's/old/new/g' file.txt              # replace all occurrences
sed 's/old/new/gi' file.txt             # case insensitive replace all
sed -i 's/localhost/0.0.0.0/g' app.cfg  # edit file in place
sed -n '10,20p' file.txt                # print lines 10 to 20
sed '/^#/d' config.txt                  # delete comment lines
sed '/^$/d' config.txt                  # delete blank lines

# cut
cut -d: -f1 /etc/passwd                 # delimiter :, print field 1
cut -d, -f2,4 data.csv                  # delimiter comma, fields 2 and 4
cut -c1-10 file.txt                     # first 10 characters of each line

# sort & uniq
sort file.txt                           # alphabetical sort
sort -n numbers.txt                     # numeric sort
sort -rn numbers.txt                    # reverse numeric sort
sort -k2 file.txt                       # sort by second column
sort file.txt | uniq                    # remove duplicate lines
sort file.txt | uniq -c                 # count occurrences of each line
sort file.txt | uniq -d                 # show only duplicate lines

# pipes — combining tools
cat /var/log/nginx/access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head -10
# → top 10 IP addresses by request count

ps aux | grep nginx | grep -v grep
# → find nginx processes, exclude the grep itself

cat /etc/passwd | cut -d: -f1 | sort
# → sorted list of all users
```

---

## Process management

```bash
ps aux                       # all running processes
ps aux | grep python         # find processes by name
ps -ef --forest              # process tree with parent-child relationships
pgrep nginx                  # get PID of process by name
pidof nginx                  # same

top                          # live process monitor (q to quit)
htop                         # better top (install: apt install htop)

kill 1234                    # send SIGTERM to PID (graceful)
kill -9 1234                 # send SIGKILL (force kill — last resort)
killall nginx                # kill all processes named nginx
pkill -f "python app.py"     # kill by full command match

# Background jobs
command &                    # run in background
jobs                         # list background jobs
fg %1                        # bring job 1 to foreground
bg %1                        # send job 1 to background
nohup command &              # run immune to hangup (survives terminal close)
disown %1                    # detach job from terminal

# Signals
# SIGTERM (15) — graceful shutdown, app can clean up
# SIGKILL (9)  — immediate kill, cannot be caught or ignored
# SIGHUP (1)   — reload config (many daemons use this)
# SIGINT (2)   — Ctrl+C
```

---

## Systemd & services

```bash
systemctl status nginx               # show service status
systemctl start nginx                # start service
systemctl stop nginx                 # stop service
systemctl restart nginx              # stop then start
systemctl reload nginx               # reload config without restart
systemctl enable nginx               # start on boot
systemctl disable nginx              # don't start on boot
systemctl is-active nginx            # just active/inactive

journalctl -u nginx                  # logs for nginx service
journalctl -u nginx -f               # follow logs
journalctl -u nginx --since "1 hour ago"
journalctl -u nginx --since "2024-01-01" --until "2024-01-02"
journalctl -p err                    # only error level and above
journalctl --disk-usage              # how much space logs are using
```

---

## Networking

```bash
# Connectivity
ping -c 4 google.com                 # send 4 packets
traceroute google.com                # trace route to host
mtr google.com                       # combined ping + traceroute (install: apt install mtr)
curl -v https://example.com          # verbose HTTP request, shows headers and TLS
curl -I https://example.com          # headers only
curl -o /dev/null -s -w "%{http_code}" https://example.com   # just the status code
wget -q -O - https://example.com     # download to stdout

# DNS
dig google.com                       # full DNS lookup
dig google.com A                     # A records only
dig google.com MX                    # MX records
dig @8.8.8.8 google.com              # query specific DNS server
nslookup google.com                  # simpler DNS lookup
host google.com                      # quick lookup

# Ports & connections
ss -tuln                             # listening TCP and UDP ports
ss -tulnp                            # same + process name (requires sudo)
netstat -tuln                        # older alternative to ss
lsof -i :80                          # what's using port 80
lsof -i :80 -i :443                  # what's using port 80 or 443
nc -zv hostname 80                   # test if port is open (netcat)
nc -zv hostname 80-443               # test port range

# Interface info
ip addr                              # show all interfaces and IPs
ip addr show eth0                    # specific interface
ip route                             # routing table
ip route get 8.8.8.8                 # which interface would be used to reach an IP
ifconfig                             # older alternative (may not be installed)

# Firewall (Ubuntu/Debian)
ufw status                           # firewall status
ufw allow 80/tcp                     # allow port 80
ufw allow from 192.168.1.0/24        # allow from subnet
ufw deny 22                          # deny SSH
```

---

## SSH

```bash
ssh user@hostname                    # basic connection
ssh -p 2222 user@hostname            # custom port
ssh -i ~/.ssh/id_ed25519 user@host   # specific key
ssh -L 8080:localhost:80 user@host   # local port forwarding
ssh -R 8080:localhost:80 user@host   # remote port forwarding
ssh -N -f user@host -L 5432:db:5432  # background tunnel, no shell

# Key management
ssh-keygen -t ed25519 -C "comment"   # generate new key
ssh-copy-id user@hostname            # copy public key to server
ssh-add ~/.ssh/id_ed25519            # add key to agent

# ~/.ssh/config example
# Host myserver
#     HostName 192.168.1.100
#     User ubuntu
#     IdentityFile ~/.ssh/id_ed25519
#     Port 22
# Then just: ssh myserver

scp file.txt user@host:/remote/path/         # copy file to remote
scp user@host:/remote/file.txt ./            # copy file from remote
scp -r ./dir/ user@host:/remote/path/        # copy directory

rsync -avz ./local/ user@host:/remote/       # sync directory (preferred over scp)
rsync -avz --delete ./local/ user@host:/remote/  # sync and delete removed files
rsync --dry-run -avz ./local/ user@host:/remote/ # preview without doing anything
```

---

## Package management

```bash
# apt (Debian/Ubuntu)
apt update                           # refresh package lists
apt upgrade                          # upgrade installed packages
apt install nginx                    # install a package
apt install -y nginx curl git        # install multiple, auto-confirm
apt remove nginx                     # remove package (keep config)
apt purge nginx                      # remove package and config
apt autoremove                       # remove unused dependencies
apt search nginx                     # search available packages
apt show nginx                       # package details
dpkg -l | grep nginx                 # check if installed

# yum/dnf (RHEL/CentOS/Fedora)
dnf update                           # update all packages
dnf install nginx                    # install
dnf remove nginx                     # remove
dnf search nginx                     # search
rpm -qa | grep nginx                 # check if installed
```

---

## Useful one-liners

```bash
# Find largest files in current directory tree
find . -type f -printf '%s %p\n' | sort -rn | head -20

# Watch a command every 2 seconds
watch -n 2 'df -h'

# Show real-time network bandwidth by interface
watch -n 1 'cat /proc/net/dev'

# Count lines in all .py files in a project
find . -name "*.py" | xargs wc -l | tail -1

# Find files modified in the last 10 minutes
find /var/log -mmin -10 -type f

# Show the 10 most recently modified files
find . -type f -printf '%T@ %p\n' | sort -rn | head -10 | awk '{print $2}'

# Repeat a command until it succeeds
until curl -s http://localhost:8080/health; do sleep 2; done

# Time how long a command takes
time ./my-script.sh

# Run command and save output to file AND show it on screen
./script.sh | tee output.log

# Extract tar.gz
tar -xzf archive.tar.gz
tar -xzf archive.tar.gz -C /target/dir/

# Create tar.gz
tar -czf archive.tar.gz ./directory/
```

---

*Part of [devops-to-ai](../../README.md) — Phase 00: The Foundation*
