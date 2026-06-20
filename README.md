# SSH Operator

通过 SSH/SFTP 远程部署项目、管理 Docker、操作宝塔面板。

## 有什么用

- 上传文件/文件夹到远程服务器
- 远程执行 docker-compose 构建和重启
- 部署前自动备份代码和数据库
- 查看服务器状态、收集日志
- 宝塔面板安装、`bt` 命令、Nginx 反代配置

## 文件结构

```
ssh-operator/
├── SKILL.md                  # Agent Skill 主指令
├── README.md                 # 本文件
├── scripts/                  # 脚本库
│   ├── _ssh.py               # SSH 连接和配置公共模块
│   ├── deploy-folder.py      # 多文件/文件夹部署
│   ├── deploy-rsync.sh       # rsync 增量同步
│   ├── backup_before_deploy.py
│   ├── server_health.py
│   ├── log_collector.py
│   ├── nginx_manager.py
│   └── bt_panel.py
├── references/               # 参考文档
│   ├── baota.md
│   ├── bt-commands.md
│   └── troubleshooting.md
├── requirements.txt
├── .env.example
└── LICENSE
```

## 3 分钟上手

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置连接信息

复制 `.env.example` 为 `.env`，填写服务器信息：

```bash
cp .env.example .env
```

```env
SSH_HOST=1.2.3.4
SSH_PORT=22
SSH_USER=root
SSH_PASS=你的密码
# 或者用密钥：SSH_KEY_PATH=/path/to/key

REMOTE_ROOT=/www/wwwroot/your-project
```

> `.env` 只存在本地，不会上传到 GitHub（已在 `.gitignore` 中排除）。

### 3. 运行脚本

例如部署项目：

```bash
# 复制脚本到项目目录时，记得同时复制 _ssh.py
cp scripts/deploy-folder.py scripts/_ssh.py ./
python deploy-folder.py
```

每个脚本顶部都有用法注释，直接看脚本里的说明即可。

## 常用命令

```bash
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
