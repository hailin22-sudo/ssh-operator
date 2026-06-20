#!/usr/bin/env bash
# 使用 rsync 增量同步多文件项目的模板脚本。
#
# 用法：
#   1. 复制此文件到项目目录（如 deploy.sh）。
#   2. 配置环境变量或修改下方的默认值：
#      - SSH_HOST
#      - SSH_PORT（默认 22）
#      - SSH_USER
#      - REMOTE_ROOT
#   3. 调整 RSYNC_OPTS 和 EXCLUDES。
#   4. 运行：bash deploy.sh
#
# 需要本地安装 rsync 和 ssh。

set -euo pipefail

SSH_HOST="${SSH_HOST:-YOUR_SERVER_IP}"
SSH_PORT="${SSH_PORT:-22}"
SSH_USER="${SSH_USER:-root}"
REMOTE_ROOT="${REMOTE_ROOT:-/www/wwwroot/your-project}"

# 要同步的本地目录（末尾带 / 表示同步目录内容）
LOCAL_SOURCE="${LOCAL_SOURCE:-./}"

# rsync 选项
RSYNC_OPTS="-avz --delete --progress"

# 排除列表（不同步的文件/目录）
EXCLUDES=(
  --exclude='.git'
  --exclude='.venv'
  --exclude='node_modules'
  --exclude='.next'
  --exclude='__pycache__'
  --exclude='*.pyc'
  --exclude='.env'
  --exclude='.env.local'
  --exclude='deploy.sh'
)

echo "=== 同步文件到 ${SSH_USER}@${SSH_HOST}:${REMOTE_ROOT} ==="
rsync ${RSYNC_OPTS} "${EXCLUDES[@]}" \
  -e "ssh -p ${SSH_PORT}" \
  "${LOCAL_SOURCE}" \
  "${SSH_USER}@${SSH_HOST}:${REMOTE_ROOT}/"

echo "=== 在服务器上执行部署命令 ==="
ssh -p "${SSH_PORT}" "${SSH_USER}@${SSH_HOST}" "cd ${REMOTE_ROOT} && docker-compose up -d --build"

echo "=== 检查服务状态 ==="
ssh -p "${SSH_PORT}" "${SSH_USER}@${SSH_HOST}" "cd ${REMOTE_ROOT} && docker-compose ps"

echo "=== 部署完成 ==="
