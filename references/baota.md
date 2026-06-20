# 宝塔面板（Baota）实操指南

官网：https://www.bt.cn

宝塔是国内最常用的 Linux 服务器运维面板，提供 Web UI 管理网站、Docker、Nginx、数据库、防火墙等。本指南聚焦在**命令行 + 自动化脚本**角度，配合 Agent 完成部署。

---

## 1. 安装宝塔 Linux 面板

### 1.1 官方推荐安装命令

以 root 身份连接服务器后执行（来自 https://www.bt.cn/new/download.html）：

```bash
if [ -f /usr/bin/curl ];then curl -sSO https://download.bt.cn/install/install_panel.sh;else wget -O install_panel.sh https://download.bt.cn/install/install_panel.sh;fi;bash install_panel.sh ed8484bec
```

安装完成后会输出：

- 面板访问地址（形如 `https://<IP>:<端口>/<安全入口>`）
- 默认用户名
- 默认密码

### 1.2 安装后常用初始化

```bash
# 查看面板默认入口、账号、密码
bt default

# 重启面板
bt restart

# 修改面板密码（交互式）
bt 5

# 查看当前面板端口
cat /www/server/panel/data/port.pl
```

### 1.3 防火墙放行

宝塔面板端口默认随机生成（常见 8888、443 等），必须在云服务器安全组放行该端口，才能通过浏览器访问。

---

## 2. `bt` 命令行工具速查

宝塔提供 `bt` 命令，可在 SSH 中不登录 Web 面板直接操作：

```bash
bt default          # 显示面板地址、账号、密码
bt restart          # 重启面板
bt stop             # 停止面板
bt start            # 启动面板
bt reload           # 重载面板
bt 5                # 修改面板密码
bt 6                # 修改面板用户名
bt 10               # 查看面板日志
bt 12               # 取消域名绑定限制
bt 13               # 取消 IP 访问限制
bt 14               # 查看面板错误日志
bt 16               # 修改面板端口
bt 22               # 取消 SSL 强制 HTTPS
bt 23               # 设置 SSL 证书
```

> 完整命令列表会随版本变化，可运行 `bt` 不带参数查看菜单。

---

## 3. 推荐项目目录与部署方式

### 3.1 Docker Compose 方式（推荐）

项目目录：`/www/wwwroot/<site-name>`

```bash
mkdir -p /www/wwwroot/<site-name>
cd /www/wwwroot/<site-name>

# 上传 docker-compose.yml、.env、代码目录后执行
docker-compose up -d --build
```

宝塔 8.x 起内置「Docker 管理器」，可在 Web 面板中查看容器、镜像、日志、重启容器。

### 3.2 宝塔「网站」+ Nginx 反向代理

适合 Next.js / Nuxt / React / Vue 等 Node 前端项目：

1. 宝塔「网站」→「添加站点」。
2. 站点目录指向 `/www/wwwroot/<site-name>`。
3. 在站点「配置文件」中追加 Nginx 反向代理：

```nginx
location / {
    proxy_pass http://127.0.0.1:3000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache_bypass $http_upgrade;
}
```

4. 如果后端在 8000 端口，路由 `/api/` 到后端：

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

5. 保存后重载 Nginx：`bt reload nginx` 或在面板中点击「重载」。

### 3.3 宝塔「Python 项目」部署

宝塔 8.x 支持直接部署 Python 项目（Flask/FastAPI/Django）：

1. 上传代码到 `/www/wwwroot/<site-name>`。
2. 宝塔「网站」→「Python 项目」→「添加 Python 项目」。
3. 选择项目路径、Python 版本、启动文件、端口。
4. 宝塔会自动创建虚拟环境并启动 gunicorn/uvicorn。
5. 通过 Nginx 反代该端口即可对外提供服务。

---

## 4. 防火墙与端口

宝塔有独立防火墙，路径：「安全」→「防火墙」。

常见需要放行的端口：

| 用途 | 端口 |
|---|---|
| HTTP | 80 |
| HTTPS | 443 |
| 宝塔面板 | 安装时随机（查看 `cat /www/server/panel/data/port.pl`） |
| Node 前端 | 3000（仅本地反代可不对外放行） |
| FastAPI 后端 | 8000（仅本地反代可不对外放行） |
| SSH | 22（或自定义） |

> 生产环境不要把 3000/8000 等应用端口直接暴露到公网，应通过 Nginx 反代 80/443。

---

## 5. SSL 证书

宝塔提供三种 SSL 方式：

1. **Let's Encrypt 免费证书**：在站点「SSL」→「Let's Encrypt」中申请。
2. **宝塔 SSL**：付费证书，面板内购买。
3. **自定义证书**：上传 `.pem`/`.key` 文件。

申请后宝塔会自动修改 Nginx 配置并监听 443。

---

## 6. 自动化场景示例

### 一键重启 Nginx

```bash
bt reload nginx
```

### 一键重启 Docker 容器（配合 docker-compose）

```bash
cd /www/wwwroot/<site-name> && docker-compose restart backend
```

### 查看所有容器状态

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

---

## 7. 常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
| 宝塔面板打不开 | 安全组未放行面板端口 | `cat /www/server/panel/data/port.pl` 查看端口，并在安全组放行 |
| 网站 502 | 反代目标未启动 | `docker-compose ps` 或 `bt reload nginx` |
| 域名访问不了 | DNS 未解析 / 防火墙 / 安全组 | 检查 A 记录、宝塔防火墙、云安全组 |
| 端口冲突 | 容器端口与宝塔默认端口冲突 | 修改 `docker-compose.yml` 的端口映射 |
| SQLite 数据库丢失 | 数据文件放在代码目录被覆盖 | 使用 Docker volume 挂载到 `/app/data` |
| 磁盘占满 | Docker build cache 累积 | `docker system prune -a -f` |

---

## 8. 参考链接

- 官网：https://www.bt.cn
- 下载安装：https://www.bt.cn/new/download.html
- 官方文档：https://docs.bt.cn
- 宝塔论坛：https://www.bt.cn/bbs
