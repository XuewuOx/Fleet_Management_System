# AGV/AMR Fleet Management System

基于 Django 的AGV车队管理系统，包含落地页、操作员登录/登出、控制台（用户管理、布局编辑）等功能。由英国纽卡斯尔诺森比亚大学工程、物理与数学学院 [EFORES team at CO-NETS lab](https://www.efores.net)团队开发。

## 技术栈

| 组件 | 版本 |
|------|------|
| Python | 3.12+ |
| Django | 6.0.3 |
| 数据库 | PostgreSQL 14+（本项目使用 16） |
| 依赖 | python-dotenv、psycopg、Pillow |


## 启动开发服务器

建议使用`tmux`创建终端，在终端里启用服务，采用tmux方式的好处是，服务长期运行，不会因为当前终端被关闭（如结束远程连接）而强制终止从该终端启动的所有进程。

### tmux 创建新终端

```bash
# 创建并进入一个名为 AGVdjango 的新会话
tmux new -s AGVdjango
```

在这个AGVdjango的终端里，进入项目根目录, 激活虚拟环境
```bash
cd Fleet_Management_System

# 激活虚拟环境
source .venv/bin/activate
```

启动服务
```bash
# 指定端口（如 8001）
python manage.py runserver 0.0.0.0:8001

# 如果不指定端口，默认端口 8000
python manage.py runserver

```

启动后访问：

- 首页：`http://127.0.0.1:8001/`
- 管理后台：`http://127.0.0.1:8001/admin/`


### tmux 常用操作
进入会话后常用快捷键：

| 操作 | 快捷键 |
|------|--------|
| 脱离会话（进程继续运行） | `Ctrl+b` 然后按 `d` |
| 新建窗口 | `Ctrl+b` 然后按 `c` |
| 切换窗口 | `Ctrl+b` 然后按窗口编号（0/1/2…） |

脱离后再次回到会话：

```bash
# 查看所有会话
tmux ls

# 重新进入 AGVdjango 会话
tmux attach -t AGVdjango
```

## 如何强制终止服务

如果不能在终端（包括 tmux 会话）中正常停止服务，可通过以下步骤强制终止：

```bash
# 1. 查找占用 8001 端口的进程
ss -lntp '( sport = :8001 )'

# 2. 终止进程（PID 以上一步输出为准）
kill <PID>
```

本次实际终止了 runserver 的父进程与子进程（1789411、1790189），验证 8001 已释放、无 runserver 进程。



## 目录结构

```
Fleet_Management_System/
├── manage.py                     # Django 命令行入口
├── requirements.txt              # Python 依赖清单
├── .env                          # 环境变量（数据库连接信息，不入库）
├── .gitignore
├── core/                         # 项目配置（settings / urls / wsgi / asgi）
│   ├── settings.py               # 全局配置（数据库、ALLOWED_HOSTS 等）
│   ├── urls.py                   # 根路由
│   ├── wsgi.py
│   └── asgi.py
├── landing_page/                 # 落地页应用
│   ├── views.py
│   ├── urls.py                   # 路由：/
│   ├── templates/landing_page/
│   └── static/
├── operator_auth/                # 操作员认证应用
│   ├── views.py                  # 登录 / 登出逻辑
│   ├── urls.py                   # 路由：/auth/login/、/auth/logout/
│   ├── templates/operator_auth/
│   └── static/
├── dashboard/                    # 主控制台应用
│   ├── models/
│   │   ├── custom_user.py        # 自定义用户模型 CustomUser（含头像、角色）
│   │   └── layout.py
│   ├── views/
│   │   ├── dashboard_views.py    # 控制台首页
│   │   ├── layout_views.py       # 布局查看/编辑/保存
│   │   └── admin_views.py        # 用户注册、资料、用户列表
│   ├── backends.py               # 用户名/邮箱登录后端
│   ├── urls.py                   # 路由：/dashboard/...
│   ├── templates/dashboard/
│   ├── static/
│   └── migrations/               # 数据库迁移文件
├── media/
│   └── profile_pictures/         # 用户头像上传目录
└── .venv/                        # Python 虚拟环境（3.12）
```

## 环境要求

- Python 3.12 及以上
- PostgreSQL 14 及以上（Django 6.0 要求，本项目实测 16.16）
- `pip` / `uv` 等包管理工具


## 应用部署

如果是第一次运行，从github代码仓库克隆代码到本地后，还需要先完成部署，安装依赖之后，才能启动服务

### 1. 准备虚拟环境

进入项目根目录
```bash
# 创建虚拟环境（要求 Python 3.12+）
python3.12 -m venv .venv

```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置数据库

在项目根目录创建 `.env` 文件（参考以下格式）：

```dotenv
DB_NAME=fleet_management_db
DB_USER=fleet_admin
DB_PASSWORD=<你的数据库密码>
DB_HOST=localhost
DB_PORT=5432
```

并在 PostgreSQL 中创建对应的用户和数据库：

```bash
sudo -u postgres psql -c "CREATE ROLE fleet_admin LOGIN PASSWORD '<你的数据库密码>';"
sudo -u postgres createdb -O fleet_admin fleet_management_db
```

### 4. 执行数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. 创建超级用户（可选，用于登录后台）

```bash
python manage.py createsuperuser
```


## 部署注意事项

1. **关闭调试模式**：生产环境必须将 `core/settings.py` 中的 `DEBUG` 设为 `False`，并妥善保管 `SECRET_KEY`，不要使用默认的 insecure key。

2. **配置 `ALLOWED_HOSTS`**：将公网 IP 或域名加入 `ALLOWED_HOSTS`，否则外部访问会被 Django 拒绝：
   ```python
   ALLOWED_HOSTS = ['your-domain.com', '你的公网IP']
   ```

3. **不要用开发服务器对外服务**：`runserver` 仅供开发测试。生产环境请使用 `gunicorn`/`uwsgi` + `nginx`：
   ```bash
   gunicorn core.wsgi:application -b 0.0.0.0:8001
   ```

4. **放行防火墙/安全组端口**：云服务器（如阿里云 ECS）需在安全组中开放对应端口（如 8001），本机防火墙也需放行。

5. **数据库版本**：Django 6.0 要求 PostgreSQL ≥ 14，请勿使用 13 及以下版本。

6. **静态文件与媒体文件**：
   - 生产环境需执行 `python manage.py collectstatic` 收集静态文件，并由 nginx 直接托管。
   - `media/` 目录存放用户上传的头像等文件，需确保目录可写，并由 nginx 配置 `MEDIA_URL` 访问。

7. **敏感信息管理**：数据库密码等敏感信息放在 `.env` 中，且 `.env` 已加入 `.gitignore`，不要提交到版本库。


