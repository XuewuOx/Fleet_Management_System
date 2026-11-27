# Django 服务器在AliCloud ECS Linux上的启动与账号管理指南

> 服务器：aliyun2（`47.94.**.**9`）
> 更新日期：2026-11-28
> 适用项目：Fleet Management System（Django 6.0.3，Python 3.12）

**Note: ** in the IP address are placeholers, replace it to the correct numbers.**

---

## 1. 当前Linux服务器端口使用情况

### 1.1 TCP 监听端口

#### 🔴 对外监听（`0.0.0.0` / `::`，外部可访问，受阿里云安全组控制）

| 端口 | 进程 | 用途 | 风险/说明 |
|------|------|------|-----------|
| 22 | sshd | SSH 登录 | 仅密钥登录，安全 |
| 80 | nginx | WordPress / 默认站点 | 建议跳转 443 |
| 443 | nginx | HTTPS（有 Cloudflare Origin 证书） | 正常 |
| 10973 | nginx | REDAIMS 系统（Basic Auth） | 有基础认证，正常 |
| **8080** | python（Django runserver） | Fleet Management 演示服务 | **高风险**：开发服务器 + 当前 `0.0.0.0` 全网监听，仅演示期间开放，结束后必须关闭或改回 `127.0.0.1` |
| 5355 | systemd-resolve | LLMNR 多播发现 | 低风险 |

#### 🟢 仅本机回环监听（`127.0.0.1` / `::1`，外部不可达）

| 端口 | 进程 | 用途 |
|------|------|------|
| 3306 | mysqld | MySQL |
| 6379 | redis-server | Redis |
| 11211 | memcached | Memcached |
| 5432 | postgres | PostgreSQL（项目数据库） |
| 25 | postfix master | SMTP（本机投递） |
| 1883 | mosquitto | MQTT |
| 8000 | uvicorn | REDAIMS 后端 |
| 20241 | cloudflared | Cloudflare Tunnel 本地入口 |
| 55762 | sshd | 当前会话的 SSH 端口转发 |
| 29523 / 22887 / 17782 / 11863 | VS Code Server | 远程开发工具 |

### 1.2 UDP 监听端口

| 端口 | 进程 | 用途 |
|------|------|------|
| 53 | systemd-resolve | 本机 DNS 解析（127.0.0.53） |
| 323 | chronyd | NTP |
| 5355 | systemd-resolve | LLMNR |
| 44367 / 5623 / 3656 / 64211 | cloudflared | Tunnel 出站 QUIC（正常） |

### 1.3 端口查询命令

```bash
# 查看所有 TCP 监听端口及进程
ss -ltnp

# 查看所有 UDP 监听端口及进程
ss -lunp

# 查看指定端口
ss -ltnp 'sport = :8080'
```

> 注：FTP（21）已于 2026-11-27 关闭并禁用（`pureftpd.service`）。

---

## 2. Django 启动方式与远程 SSH 连接

### 2.1 项目信息

- 项目目录：`/home/conets/groupshare/xuewuOx-AliBJ/Fleet_Management_System`（已由 `/root/xuewuOx-AliBJ/Fleet_Management_System` 迁入）
- 虚拟环境：项目内 `.venv`（基于 uv 管理的 Python 3.12）
- 依赖：`Django==6.0.3`、`python-dotenv`、`psycopg[binary]`、`Pillow`
- 数据库：PostgreSQL（配置见项目根目录 `.env`）

### 2.2 方式一：内部调试（仅本机监听 + SSH 隧道，推荐日常使用）

Django 只监听 `127.0.0.1:8080`，外部无法直接访问，必须通过 SSH 隧道从本机电脑访问。

**第一步：服务器上启动 Django（只监听本机）**

```bash
cd /home/conets/groupshare/xuewuOx-AliBJ/Fleet_Management_System
source .venv/bin/activate
python manage.py runserver 127.0.0.1:8080
```

**第二步：本机电脑建立 SSH 隧道**

(1) 如果本地机器已经使用**VSCode Remote-SSH**远程连接了Linux服务器，应该是自动进行8080端口转发，因此本机可以直接用本地端口，如`http://localhost:8080`实现访问, 无需手动敲隧道命令。

(2) 如果本地没有使用VSCode进行远程连接，可以手动创建一个SSH隧道，进行端口转发。 
本地Windows (或者Linux)，在powershell 或者bash执行
```bash
ssh -L 8080:127.0.0.1:8080 conets@47.94.142.219
```

- `8080`（第一个）：本机电脑要监听的端口，可以修改为其他端口，如8081等
- `127.0.0.1`：站在**服务器**视角解析的地址（即服务器自己的回环）
- `8080`（最后一个）：服务器上的目标端口（Django）

**第三步：浏览器访问**

```
http://localhost:8080
```

> 隧道命令会占用前台窗口，关闭窗口或按 `Ctrl+C` 即断开。不想占用窗口可用后台方式：
>
> ```bash
> ssh -N -f -L 8080:127.0.0.1:8080 conets@47.94.142.219
> ```
>
> `-N` 不执行远程命令，`-f` 认证后转入后台。



### 2.3 方式二：对外演示（全网监听 + DEBUG=false，临时使用）

演示期间让 Django 监听 `0.0.0.0:8080`，通过域名 `agv.efores.net:8080` 或 IP 对外访问；演示结束立即关闭。

```bash
cd /home/conets/groupshare/xuewuOx-AliBJ/Fleet_Management_System
source .venv/bin/activate
DEBUG=false python manage.py runserver 0.0.0.0:8080 --insecure
```

- `DEBUG=false`：关闭调试模式，避免暴露堆栈/源码/配置
- `--insecure`：`DEBUG=false` 时仍由 runserver 提供静态文件（CSS/图片），否则页面无样式
- `ALLOWED_HOSTS` 已包含 `47.94.142.219`、`agv.efores.net`、`agv.efores.net:8080`

**停止服务**：前台按 `Ctrl+C`；或后台运行时：

```bash
# 找到 8080 进程并结束
ss -ltnp 'sport = :8080'          # 拿到 PID
kill -9 <PID>
```

### 2.4 ⚠️ 重要：DEBUG 由环境变量控制，关闭时必须用小写 `false`

`core/settings.py` 已改为读取环境变量：

```python
DEBUG = os.getenv('DEBUG', 'True') == 'True'
```

该比较**大小写敏感、精确匹配**，只有字符串恰好等于 `True` 时调试才开启：

| 命令里的写法 | 实际结果 |
|--------------|----------|
| `DEBUG=false ...`（小写） | `DEBUG = False` ✅ 关闭调试 |
| `DEBUG=False ...` | `DEBUG = False` ✅ 关闭调试 |
| `DEBUG=True ...`（大写 T） | `DEBUG = True` ✅ 开启调试 |
| `DEBUG=true ...`（小写 t） | `DEBUG = False` ⚠️ 不会开启调试 |
| 不传 `DEBUG` | `DEBUG = True`（默认） |

> 结论：**对外演示关闭调试用 `DEBUG=false`（小写）**；日常调试直接不传该变量即可（默认开启）。

### 2.5 一键命令汇总

```bash
# 内部调试（本机监听）
cd /home/conets/groupshare/xuewuOx-AliBJ/Fleet_Management_System && source .venv/bin/activate && python manage.py runserver 127.0.0.1:8080

# 对外演示（全网监听，结束后务必关闭）
cd /home/conets/groupshare/xuewuOx-AliBJ/Fleet_Management_System && source .venv/bin/activate && DEBUG=false python manage.py runserver 0.0.0.0:8080 --insecure

# 本机电脑 SSH 隧道
ssh -L 8080:127.0.0.1:8080 conets@47.94.142.219

# 本机电脑 SSH 隧道（后台）
ssh -N -f -L 8080:127.0.0.1:8080 conets@47.94.142.219
```

### 2.6 ⚠️ 项目目录迁移后：修复 `.venv` 硬编码路径

`.venv` 的 `activate` 脚本和部分入口脚本（`django-admin`、`dotenv`、`sqlformat`）内写死了**绝对路径**。项目目录一旦变更，`source .venv/bin/activate` 会静默失效（`python` 回退到系统 Python 3.6），导致 `ModuleNotFoundError: No module named 'dotenv'`。

迁移后必须执行一次路径替换：

```bash
cd /home/conets/groupshare/xuewuOx-AliBJ/Fleet_Management_System
OLD=/root/xuewuOx-AliBJ/Fleet_Management_System
NEW=/home/conets/groupshare/xuewuOx-AliBJ/Fleet_Management_System
sed -i "s#$OLD#$NEW#g" .venv/bin/activate .venv/bin/activate.bat .venv/bin/activate.csh .venv/bin/activate.fish .venv/bin/activate.nu .venv/bin/django-admin .venv/bin/dotenv .venv/bin/sqlformat
```

验证：

```bash
source .venv/bin/activate
which python            # 应为 .../Fleet_Management_System/.venv/bin/python
python --version        # 应为 Python 3.12.x
python manage.py check  # System check identified no issues
```

> 另一种更彻底的做法是删除 `.venv` 后用 `uv sync` 重建（需 `uv` 可用且能联网）。

---

## 3. 账号与共享目录设计

### 3.1 设计原理

项目代码放在公共账户 `conets` 的家目录下的 `groupshare` 目录中，通过**组 `group_conets` + setgid + 默认 ACL** 实现多人共享同一份代码：

| 对象 | 说明 |
|------|------|
| `root` | 超级管理员，天然可读写系统内任何文件，无需额外配置 |
| `group_conets` | 共享开发组（gid 1005），成员：`conets`、`efores` |
| `conets` | 公共账户（uid 1005），家目录 `/home/conets`，是共享代码的"宿主" |
| `efores` | 开发账户（uid 1006），隶属于 `group_conets`，可读写共享目录 |
| `groupshare` | `/home/conets/groupshare`，共享目录（`2775` + 默认 ACL） |

**三个关键机制：**

1. **组共享**：所有开发账户都加入 `group_conets`，共享目录属组为 `group_conets`，组内成员即可读写。
2. **setgid（目录上的 `s` 位）**：在共享目录内新建的文件/子目录**自动继承 `group_conets` 组**，不会变成个人私有组。
3. **默认 ACL**：`default:group::rwx` 保证新建文件/子目录对 `group_conets` 组自动可读写，实现成员间**互相修改对方创建的文件**，而不只是删除。

### 3.2 目录权限一览

```
/home/conets             drwxr-x---  (750)  conets:group_conets
    └── groupshare       drwxrwsr-x+ (2775) conets:group_conets   ← setgid + 组可写 + ACL
```

- `/home/conets` 保持 `750`（组只读可进入、**不可写**）：既让组员能 `cd` 进 `groupshare`，又避免 sshd `StrictModes` 因"家目录组可写"而拒绝 `conets` 密钥登录。
- `/home/conets/groupshare` 为 `2775` + 默认 ACL：真正的共享读写区。

### 3.3 使用方法

```bash
# 开发账户登录后进入共享目录
ssh efores@47.94.142.219
cd /home/conets/groupshare

# 维护项目（已迁入）
cd /home/conets/groupshare/Fleet_Management_System
```

- 两个账户当前**密码已锁定**，需先设密码（`passwd conets` / `passwd efores`）或添加 SSH 公钥到各自 `~/.ssh/authorized_keys`。
- 组内任何人新建的文件都会自动组可写，互相可直接编辑。

### 3.4 常用命令

```bash
# —— 查看 ——
getent group group_conets                 # 查看组信息（成员列表在最后）
id conets; id efores                      # 查看用户及其所属组
ls -ld /home/conets /home/conets/groupshare   # 查看目录权限
getfacl /home/conets/groupshare           # 查看共享目录 ACL

# —— 新增开发账户（加入共享组）——
useradd -m -g group_conets -s /bin/bash <用户名>
passwd <用户名>                            # 设密码（或改用 SSH 公钥）

# —— 切换用户 ——
su - conets
su - efores

# —— 以某用户身份测试权限 ——
runuser -u efores -- touch /home/conets/groupshare/test.txt

# —— git 权限协同（组内多人共用一个仓库时）——
cd /home/conets/groupshare/Fleet_Management_System
git config core.sharedRepository group

# —— 共享目录权限维护 ——
chown conets:group_conets /home/conets/groupshare
chmod 2775 /home/conets/groupshare
setfacl -d -m g::rwx /home/conets/groupshare
```

> 建议每个开发账户在 `~/.bashrc` 中设置 `umask 0002`，使登录 shell 下新建文件默认组可写（已为 `conets`、`efores` 配置）。
