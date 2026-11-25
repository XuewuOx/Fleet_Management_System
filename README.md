# AGV/AMR Fleet Management System

A Django-based AGV fleet management system featuring a landing page, operator login/logout, and a dashboard (user management, layout editing, etc.), developed by the [EFORES team at CO-NETS lab](https://www.efores.net), the School of Engineering, Physics and Mathematics, Northumbria University, Newcastle, UK.

## Tech Stack

| Component | Version |
|-----------|---------|
| Python | 3.12+ |
| Django | 6.0.3 |
| Database | PostgreSQL 14+ (this project uses 16) |
| Dependencies | python-dotenv, psycopg, Pillow |


## Starting the Development Server

It is recommended to use `tmux` to create a terminal and run the service in it. The advantage of using tmux is that the service keeps running for a long time and will not be forcibly terminated when the terminal is closed (e.g., ending a remote connection).

### Creating a New Terminal with tmux

```bash
# Create and enter a new session named AGVdjango
tmux new -s AGVdjango
```

Inside the AGVdjango terminal, enter the project root directory and activate the virtual environment:

```bash
cd Fleet_Management_System

# Activate the virtual environment
source .venv/bin/activate
```

Start the service:

```bash
# Specify a port (e.g., 8001)
python manage.py runserver 0.0.0.0:8001

# If no port is specified, the default port is 8000
python manage.py runserver

```

After startup, visit:

- Home page: `http://127.0.0.1:8001/`
- Admin site: `http://127.0.0.1:8001/admin/`


### Common tmux Operations

Shortcuts available after entering a session:

| Operation | Shortcut |
|-----------|----------|
| Detach from the session (process keeps running) | `Ctrl+b` then `d` |
| Create a new window | `Ctrl+b` then `c` |
| Switch windows | `Ctrl+b` then the window number (0/1/2…) |

To return to the session after detaching:

```bash
# List all sessions
tmux ls

# Re-enter the AGVdjango session
tmux attach -t AGVdjango
```

## How to Force-Terminate the Service

If the service cannot be stopped normally from the terminal (including a tmux session), force-terminate it with the following steps:

```bash
# 1. Find the process occupying port 8001
ss -lntp '( sport = :8001 )'

# 2. Kill the process (use the PID from the output of the previous step)
kill <PID>
```

After termination, verify that port 8001 has been released and that no `runserver` processes remain.


## Directory Structure

```
Fleet_Management_System/
├── manage.py                     # Django command-line entry point
├── requirements.txt              # Python dependency list
├── .env                          # Environment variables (DB connection info, not committed)
├── .gitignore
├── core/                         # Project configuration (settings / urls / wsgi / asgi)
│   ├── settings.py               # Global configuration (database, ALLOWED_HOSTS, etc.)
│   ├── urls.py                   # Root URL configuration
│   ├── wsgi.py
│   └── asgi.py
├── landing_page/                 # Landing page app
│   ├── views.py
│   ├── urls.py                   # Route: /
│   ├── templates/landing_page/
│   └── static/
├── operator_auth/                # Operator authentication app
│   ├── views.py                  # Login / logout logic
│   ├── urls.py                   # Routes: /auth/login/, /auth/logout/
│   ├── templates/operator_auth/
│   └── static/
├── dashboard/                    # Main dashboard app
│   ├── models/
│   │   ├── custom_user.py        # Custom user model CustomUser (avatar, role)
│   │   └── layout.py
│   ├── views/
│   │   ├── dashboard_views.py    # Dashboard index
│   │   ├── layout_views.py       # Layout view/edit/save
│   │   └── admin_views.py        # User registration, profile, user list
│   ├── backends.py               # Username/email login backend
│   ├── urls.py                   # Routes: /dashboard/...
│   ├── templates/dashboard/
│   ├── static/
│   └── migrations/               # Database migration files
├── media/
│   └── profile_pictures/         # User profile picture upload directory
└── .venv/                        # Python virtual environment (3.12)
```

## Requirements

- Python 3.12 or higher
- PostgreSQL 14 or higher (required by Django 6.0; this project is tested with 16.16)
- Package managers such as `pip` / `uv`


## Application Deployment

When running for the first time, after cloning the code from the GitHub repository, you must complete the deployment and install dependencies before starting the service.

### 1. Prepare the Virtual Environment

Enter the project root directory:

```bash
# Create a virtual environment (requires Python 3.12+)
python3.12 -m venv .venv

```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the Database

Create a `.env` file in the project root directory (see the format below):

```dotenv
DB_NAME=fleet_management_db
DB_USER=fleet_admin
DB_PASSWORD=<your-database-password>
DB_HOST=localhost
DB_PORT=5432
```

Then create the corresponding user and database in PostgreSQL:

```bash
sudo -u postgres psql -c "CREATE ROLE fleet_admin LOGIN PASSWORD '<your-database-password>';"
sudo -u postgres createdb -O fleet_admin fleet_management_db
```

### 4. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a Superuser (optional, for logging into the admin site)

```bash
python manage.py createsuperuser
```


## Deployment Notes

1. **Turn off debug mode**: In production, set `DEBUG` to `False` in `core/settings.py` and keep `SECRET_KEY` safe. Do not use the default insecure key.

2. **Configure `ALLOWED_HOSTS`**: Add your public IP or domain to `ALLOWED_HOSTS`, otherwise external access will be rejected by Django:
   ```python
   ALLOWED_HOSTS = ['your-domain.com', 'your-public-ip']
   ```

3. **Do not expose the development server**: `runserver` is for development and testing only. In production, use `gunicorn`/`uwsgi` + `nginx`:
   ```bash
   gunicorn core.wsgi:application -b 0.0.0.0:8001
   ```

4. **Open firewall/security group ports**: For cloud servers (e.g., Alibaba Cloud ECS), open the corresponding port (e.g., 8001) in the security group; the local firewall must also allow it.

5. **Database version**: Django 6.0 requires PostgreSQL ≥ 14. Do not use version 13 or lower.

6. **Static and media files**:
   - In production, run `python manage.py collectstatic` to collect static files and serve them directly via nginx.
   - The `media/` directory stores user-uploaded files such as avatars. Make sure the directory is writable and configure `MEDIA_URL` in nginx for access.

7. **Sensitive information management**: Keep sensitive information such as database passwords in `.env`. The `.env` file is already added to `.gitignore`; do not commit it to the repository.


## Creditors
Xuewu Dai (xuewuOx)
Hpone
Yar Zar