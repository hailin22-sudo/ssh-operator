# SSH Operator

> 让 AI Agent 自动登录你的服务器，完成部署、重启、看日志、配 Nginx、管宝塔面板。

[![TRAE](https://img.shields.io/badge/TRAE-compatible-blue)](https://trae.ai)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-compatible-orange)](https://claude.ai/code)
[![Codex](https://img.shields.io/badge/OpenAI%20Codex-compatible-green)](https://openai.com/codex)
[![Cursor](https://img.shields.io/badge/Cursor-compatible-black)](https://cursor.sh)

**SSH Operator** 是一个跨平台 Agent Skill。把它丢给 TRAE、Claude Code、Codex 或 Cursor，它们就能通过 SSH/SFTP 连接你的 Linux 服务器，自动执行部署、Docker 管理、日志排查、Nginx 配置、宝塔面板操作等任务。

你不需要手写一堆部署脚本，只要告诉 Agent：「把最新代码部署到我的服务器」，它就会按规范完成备份 → 上传 → 重启 → 验证。

---

## 能做什么

- **自动部署**：上传文件或整个文件夹，远程执行 `docker-compose up -d --build`
- **修改远程网站代码**：SSH 登录后直接编辑服务器上的博客/网站源码
- **自动发布文章**：探测 WordPress/Ghost/Halo 等博客 API，用 Python 脚本发布 Markdown 文章
- **部署前备份**：自动备份代码、Nginx 配置、Docker volumes、SQLite 数据库
- **健康检查**：CPU、内存、磁盘、Docker、Nginx、HTTP 接口一键检查
- **日志收集**：把 Docker、Nginx、宝塔日志拉到本地分析
- **宝塔适配**：安装宝塔、查看面板信息、重载 Nginx、查看 Docker 状态
- **Nginx 管理**：查看/备份站点配置，追加 `/api/` 反向代理

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置服务器信息

```bash
cp .env.example .env
```

编辑 `.env`：

```env
SSH_HOST=1.2.3.4
SSH_PORT=22
SSH_USER=root
SSH_PASS=你的密码
# 或 SSH_KEY_PATH=/path/to/key

REMOTE_ROOT=/www/wwwroot/your-project
```

> `.env` 只存在本地，不会上传到 GitHub。

### 3. 让 Agent 接管

把本 Skill 目录配置进你的 Agent（TRAE、Claude Code、Codex、Cursor），然后说：

> 「把当前项目部署到我的服务器，先备份再重启。」

Agent 会读取 `.env`，调用 `scripts/` 下的脚本自动完成。

---

## 文件结构

```
ssh-operator/
├── SKILL.md                  # Agent 主指令
├── scripts/                  # 可执行脚本
│   ├── _ssh.py               # SSH 连接 + 配置加载公共模块
│   ├── deploy-folder.py      # 多文件/文件夹部署
│   ├── deploy-rsync.sh       # rsync 增量同步
│   ├── blog_api_probe.py     # 探测博客发布 API
│   ├── publish_post.py       # 发布 Markdown 文章到 WordPress/Ghost
│   ├── backup_before_deploy.py
│   ├── server_health.py
│   ├── log_collector.py
│   ├── nginx_manager.py
│   └── bt_panel.py
├── references/               # 详细参考
│   ├── baota.md
│   ├── bt-commands.md
│   ├── blog_apis.md          # 博客 API 速查
│   └── troubleshooting.md
├── requirements.txt
├── .env.example
└── LICENSE
```

---

## 常用命令

```bash
# 探测博客发布 API
python scripts/blog_api_probe.py --url https://your-blog.com

# 发布 Markdown 文章
python scripts/publish_post.py --platform wordpress --file post.md --title "标题" --status publish

# 修改远程网站代码（Agent 会 SSH 登录后直接编辑）
# 例如：修改服务器上的 theme/style.css

# 健康检查
python scripts/server_health.py --url http://1.2.3.4:8000/api/v1/health

# 部署前备份
python scripts/backup_before_deploy.py --db-path /www/wwwroot/your-project/data/app.db

# 查看/追加 Nginx 反代
python scripts/nginx_manager.py show --site example.com
python scripts/nginx_manager.py add-proxy --site example.com --path /api/ --target http://127.0.0.1:8000/

# 宝塔操作
python scripts/bt_panel.py info
python scripts/bt_panel.py reload-nginx
```

---

## 兼容平台

- [TRAE](https://trae.ai)
- [Claude Code](https://claude.ai/code)
- [OpenAI Codex](https://openai.com/codex)
- [Cursor](https://cursor.sh)

遵循 [Agent Skills](https://agentskills.io/specification) 开放规范。
