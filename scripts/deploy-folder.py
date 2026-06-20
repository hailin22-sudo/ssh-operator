#!/usr/bin/env python3
"""
通用多文件 SSH/SFTP 部署脚本模板。

用法：
  1. 复制此文件到项目目录（如 deploy.py）。
  2. 配置 .env 文件或环境变量（见 .env.example）。
  3. 调整下方的 FILES_TO_UPLOAD 和 POST_DEPLOY_COMMANDS。
  4. 运行：python deploy.py

依赖：pip install -r requirements.txt
"""
import sys
from pathlib import Path

from _ssh import connect, load_config, run

# ==================== 配置区 ====================
# 要上传的文件/文件夹列表。每一项是 (本地路径, 远程相对路径)。
# 本地是文件夹时会递归上传。
FILES_TO_UPLOAD = [
    # ("backend/app/api/v1/interview.py", "backend/app/api/v1/interview.py"),
    # ("frontend/.next", "frontend/.next"),
]

# 部署后要在服务器上执行的命令（按顺序）
POST_DEPLOY_COMMANDS = [
    # "docker-compose stop backend",
    # "docker-compose rm -f backend",
    # "docker-compose build backend",
    # "docker-compose up -d backend",
]
# =================================================


def upload_path(sftp, local: str, remote: str, remote_root: str):
    """上传单个文件或递归上传文件夹。"""
    local_path = Path(local)
    remote_abs = f"{remote_root}/{remote}".replace("\\", "/")

    if local_path.is_file():
        parent = str(Path(remote_abs).parent).replace("\\", "/")
        run(sftp.ssh, f"mkdir -p {parent}")
        print(f"上传文件: {local} -> {remote_abs}")
        sftp.put(str(local_path), remote_abs)
    elif local_path.is_dir():
        run(sftp.ssh, f"mkdir -p {remote_abs}")
        for item in local_path.rglob("*"):
            rel = item.relative_to(local_path).as_posix()
            target = f"{remote_abs}/{rel}"
            if item.is_dir():
                run(sftp.ssh, f"mkdir -p {target}")
            else:
                print(f"上传文件: {item} -> {target}")
                sftp.put(str(item), target)
    else:
        print(f"[警告] 本地路径不存在: {local_path}")


def main() -> int:
    if not FILES_TO_UPLOAD and not POST_DEPLOY_COMMANDS:
        print("请先在脚本内配置 FILES_TO_UPLOAD 和 POST_DEPLOY_COMMANDS。")
        return 1

    cfg = load_config()
    client = connect(cfg)
    sftp = client.open_sftp()

    try:
        for local, remote in FILES_TO_UPLOAD:
            upload_path(sftp, local, remote, cfg.remote_root)

        for cmd in POST_DEPLOY_COMMANDS:
            run(client, f"cd {cfg.remote_root} && {cmd}")

        print("\n=== 服务状态 ===")
        run(client, f"cd {cfg.remote_root} && docker-compose ps")

        print("\n=== 磁盘使用 ===")
        run(client, "df -h / | tail -n 1")
    finally:
        sftp.close()
        client.close()

    print("\n部署完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
