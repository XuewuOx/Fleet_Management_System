# Django Server Startup & Account Management Guide on Alibaba Cloud ECS Linux

> Server: aliyun2 (`47.94.**.**9`)
> Last updated: 2026-11-28
> Project: Fleet Management System (Django 6.0.3, Python 3.12)

**Note: ** in the IP address are placeholers, replace it to the correct numbers.**
 
---

## 1. Current Linux Server Port Usage

### 1.1 TCP Listening Ports

#### 🔴 Publicly listening (`0.0.0.0` / `::` — externally reachable, controlled by Alibaba Cloud security groups)

| Port | Process | Purpose | Risk / Notes |
|------|---------|---------|--------------|
| 22 | sshd | SSH login | Key-only login, secure |
| 80 | nginx | WordPress / default site | Consider redirecting to 443 |
| 443 | nginx | HTTPS (with Cloudflare Origin certificate) | Normal |
| 10973 | nginx | REDAIMS system (Basic Auth) | Basic auth enabled, normal |
| **8080** | python (Django runserver) | Fleet Management demo service | **High risk**: development server + currently listening on `0.0.0.0`. Only keep open during demos; close it or switch back to `127.0.0.1` when done |
| 5355 | systemd-resolve | LLMNR multicast discovery | Low risk |

#### 🟢 Loopback only (`127.0.0.1` / `::1` — not externally reachable)

| Port | Process | Purpose |
|------|---------|---------|
| 3306 | mysqld | MySQL |
| 6379 | redis-server | Redis |
| 11211 | memcached | Memcached |
| 5432 | postgres | PostgreSQL (project database) |
| 25 | postfix master | SMTP (local delivery) |
| 1883 | mosquitto | MQTT |
| 8000 | uvicorn | REDAIMS backend |
| 20241 | cloudflared | Cloudflare Tunnel local endpoint |
| 55762 | sshd | SSH port forwarding of the current session |
| 29523 / 22887 / 17782 / 11863 | VS Code Server | Remote development tooling |

### 1.2 UDP Listening Ports

| Port | Process | Purpose |
|------|---------|---------|
| 53 | systemd-resolve | Local DNS resolution (127.0.0.53) |
| 323 | chronyd | NTP |
| 5355 | systemd-resolve | LLMNR |
| 44367 / 5623 / 3656 / 64211 | cloudflared | Tunnel outbound QUIC (normal) |

### 1.3 Port Query Commands

```bash
# List all TCP listening ports and their processes
ss -ltnp

# List all UDP listening ports and their processes
ss -lunp

# Check a specific port
ss -ltnp 'sport = :8080'
```

> Note: FTP (21) was shut down and disabled on 2026-11-27 (`pureftpd.service`).

---

## 2. Django Startup Methods and Remote SSH Access

### 2.1 Project Info

- Project directory: `/home/conets/groupshare/xuewuOx-AliBJ/Fleet_Management_System` (migrated from `/root/xuewuOx-AliBJ/Fleet_Management_System`)
- Virtual environment: project-local `.venv` (uv-managed Python 3.12)
- Dependencies: `Django==6.0.3`, `python-dotenv`, `psycopg[binary]`, `Pillow`
- Database: PostgreSQL (configuration in the project root `.env`)

### 2.2 Method 1: Internal debugging (loopback only + SSH tunnel, recommended for daily use)

Django only listens on `127.0.0.1:8080`, so it is not directly reachable from outside. You must access it from your local machine through an SSH tunnel.

**Step 1: Start Django on the server (loopback only)**

```bash
cd /home/conets/groupshare/xuewuOx-AliBJ/Fleet_Management_System
source .venv/bin/activate
python manage.py runserver 127.0.0.1:8080
```

**Step 2: Set up an SSH tunnel from your local machine**

(1) If your local machine is already connected to the Linux server via **VS Code Remote-SSH**, port `8080` is usually forwarded automatically, so you can access it locally directly at `http://localhost:8080` without manually creating a tunnel.

(2) If you are not using VS Code for the remote connection, create an SSH tunnel manually. On local Windows (or Linux), run the following in PowerShell or bash:

```bash
ssh -L 8080:127.0.0.1:8080 conets@47.94.**.**9
```

- `8080` (first): the port to listen on your local machine (can be changed, e.g. `8081`)
- `127.0.0.1`: the address resolved from the **server's** perspective (i.e. the server's own loopback)
- `8080` (last): the target port on the server (Django)

**Step 3: Open in your browser**

```
http://localhost:8080
```

> The tunnel command occupies the foreground window; closing the window or pressing `Ctrl+C` disconnects it. To run it in the background:
>
> ```bash
> ssh -N -f -L 8080:127.0.0.1:8080 conets@47.94.**.**9
> ```
>
> `-N` does not execute a remote command, and `-f` sends the process to the background after authentication.

### 2.3 Method 2: Public demo (all interfaces + DEBUG=false, temporary use)

During a demo, let Django listen on `0.0.0.0:8080` and serve via the domain `agv.efores.net:8080` or the IP. Shut it down immediately when the demo ends.

```bash
cd /home/conets/groupshare/xuewuOx-AliBJ/Fleet_Management_System
source .venv/bin/activate
DEBUG=false python manage.py runserver 0.0.0.0:8080 --insecure
```

- `DEBUG=false`: disables debug mode, avoiding exposure of stack traces / source code / configuration
- `--insecure`: makes runserver keep serving static files (CSS/images) when `DEBUG=false`; otherwise the pages lose all styling
- `ALLOWED_HOSTS` already includes `47.94.**.**9`, `agv.efores.net`, `agv.efores.net:8080`

**Stopping the service**: press `Ctrl+C` in the foreground; or, if running in the background:

```bash
# Find the 8080 process and terminate it
ss -ltnp 'sport = :8080'          # get the PID
kill -9 <PID>
```

### 2.4 ⚠️ Important: DEBUG is controlled by an environment variable — use lowercase `false` to disable it

`core/settings.py` reads the environment variable:

```python
DEBUG = os.getenv('DEBUG', 'True') == 'True'
```

The comparison is **case-sensitive and exact**; debug mode is only enabled when the string is exactly `True`:

| Command | Actual result |
|---------|---------------|
| `DEBUG=false ...` (lowercase) | `DEBUG = False` ✅ debug off |
| `DEBUG=False ...` | `DEBUG = False` ✅ debug off |
| `DEBUG=True ...` (capital T) | `DEBUG = True` ✅ debug on |
| `DEBUG=true ...` (lowercase t) | `DEBUG = False` ⚠️ debug NOT enabled |
| no `DEBUG` variable | `DEBUG = True` (default) |

> Conclusion: **use `DEBUG=false` (lowercase) for public demos**; for daily debugging, simply omit the variable (debug on by default).

### 2.5 One-Liner Command Summary

```bash
# Internal debugging (loopback only)
cd /home/conets/groupshare/xuewuOx-AliBJ/Fleet_Management_System && source .venv/bin/activate && python manage.py runserver 127.0.0.1:8080

# Public demo (all interfaces — be sure to shut it down afterwards)
cd /home/conets/groupshare/xuewuOx-AliBJ/Fleet_Management_System && source .venv/bin/activate && DEBUG=false python manage.py runserver 0.0.0.0:8080 --insecure

# Local SSH tunnel
ssh -L 8080:127.0.0.1:8080 conets@47.94.**.**9

# Local SSH tunnel (background)
ssh -N -f -L 8080:127.0.0.1:8080 conets@47.94.**.**9
```

### 2.6 ⚠️ After moving the project directory: fix hardcoded paths in `.venv`

The `.venv` `activate` scripts and some entry-point scripts (`django-admin`, `dotenv`, `sqlformat`) contain hardcoded **absolute paths**. Once the project directory changes, `source .venv/bin/activate` silently fails (and `python` falls back to the system Python 3.6), causing `ModuleNotFoundError: No module named 'dotenv'`.

After moving the project, run a one-time path replacement:

```bash
cd /home/conets/groupshare/xuewuOx-AliBJ/Fleet_Management_System
OLD=/root/xuewuOx-AliBJ/Fleet_Management_System
NEW=/home/conets/groupshare/xuewuOx-AliBJ/Fleet_Management_System
sed -i "s#$OLD#$NEW#g" .venv/bin/activate .venv/bin/activate.bat .venv/bin/activate.csh .venv/bin/activate.fish .venv/bin/activate.nu .venv/bin/django-admin .venv/bin/dotenv .venv/bin/sqlformat
```

Verify:

```bash
source .venv/bin/activate
which python            # should be .../Fleet_Management_System/.venv/bin/python
python --version        # should be Python 3.12.x
python manage.py check  # System check identified no issues
```

> A more thorough alternative is to delete `.venv` and rebuild it with `uv sync` (requires `uv` to be available and network access).

---

## 3. Accounts and Shared Directory Design

### 3.1 Design Principles

The project code lives in the `groupshare` directory under the home directory of the shared account `conets`, using **group `group_conets` + setgid + default ACL** so multiple people can share the same codebase:

| Object | Description |
|--------|-------------|
| `root` | Superuser; can read/write any file on the system with no extra setup |
| `group_conets` | Shared development group (gid 1005); members: `conets`, `efores` |
| `conets` | Shared account (uid 1005), home `/home/conets`, "owner" of the shared code |
| `efores` | Developer account (uid 1006), member of `group_conets`, can read/write the shared directory |
| `groupshare` | `/home/conets/groupshare`, the shared directory (`2775` + default ACL) |

**Three key mechanisms:**

1. **Group sharing**: all developer accounts join `group_conets`; the shared directory's group is `group_conets`, so group members can read and write.
2. **setgid (the `s` bit on the directory)**: new files/subdirectories created inside the shared directory **automatically inherit the `group_conets` group** instead of becoming the creator's private group.
3. **Default ACL**: `default:group::rwx` ensures new files/subdirectories are automatically read/writable by the `group_conets` group, so members can **modify each other's files**, not just delete them.

### 3.2 Directory Permission Overview

```
/home/conets             drwxr-x---  (750)  conets:group_conets
    └── groupshare       drwxrwsr-x+ (2775) conets:group_conets   ← setgid + group-writable + ACL
```

- `/home/conets` stays `750` (group can enter and read, but **not write**): this lets group members `cd` into `groupshare` while avoiding sshd `StrictModes` rejecting `conets` key login because the home directory is group-writable.
- `/home/conets/groupshare` is `2775` + default ACL: the actual shared read/write area.

### 3.3 Usage

```bash
# After logging in as a developer, enter the shared directory
ssh efores@47.94.**.**9
cd /home/conets/groupshare

# Maintain the project (already migrated)
cd /home/conets/groupshare/Fleet_Management_System
```

- The passwords of both accounts are currently **locked**; set a password first (`passwd conets` / `passwd efores`) or add SSH public keys to each `~/.ssh/authorized_keys`.
- Any file created by a group member is automatically group-writable, so members can edit each other's files directly.

### 3.4 Common Commands

```bash
# —— Inspection ——
getent group group_conets                 # show group info (member list at the end)
id conets; id efores                      # show users and their groups
ls -ld /home/conets /home/conets/groupshare   # show directory permissions
getfacl /home/conets/groupshare           # show the shared directory ACL

# —— Add a developer account (join the shared group) ——
useradd -m -g group_conets -s /bin/bash <username>
passwd <username>                         # set a password (or use an SSH key instead)

# —— Switch user ——
su - conets
su - efores

# —— Test permissions as a specific user ——
runuser -u efores -- touch /home/conets/groupshare/test.txt

# —— Git permission coordination (multiple people sharing one repo) ——
cd /home/conets/groupshare/Fleet_Management_System
git config core.sharedRepository group

# —— Shared directory permission maintenance ——
chown conets:group_conets /home/conets/groupshare
chmod 2775 /home/conets/groupshare
setfacl -d -m g::rwx /home/conets/groupshare
```

> Recommended: set `umask 0002` in each developer account's `~/.bashrc` so that new files in a login shell are group-writable by default (already configured for `conets` and `efores`).
