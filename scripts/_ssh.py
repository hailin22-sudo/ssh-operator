"""SSH 连接和配置加载公共模块。"""
import os
from dataclasses import dataclass

import paramiko
from dotenv import load_dotenv

load_dotenv()


@dataclass
class SSHConfig:
    host: str
    port: int
    user: str
    password: str
    key_path: str
    remote_root: str
    backup_dir: str
    local_log_dir: str


def load_config() -> SSHConfig:
    """从环境变量加载 SSH 配置。"""
    return SSHConfig(
        host=os.getenv("SSH_HOST", "YOUR_SERVER_IP"),
        port=int(os.getenv("SSH_PORT", "22")),
        user=os.getenv("SSH_USER", "root"),
        password=os.getenv("SSH_PASS", ""),
        key_path=os.getenv("SSH_KEY_PATH", ""),
        remote_root=os.getenv("REMOTE_ROOT", "/www/wwwroot/your-project"),
        backup_dir=os.getenv("BACKUP_DIR", "/www/backup"),
        local_log_dir=os.getenv("LOCAL_LOG_DIR", "./logs"),
    )


def connect(cfg: SSHConfig, timeout: int = 20) -> paramiko.SSHClient:
    """根据配置建立 SSH 连接。"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    if cfg.key_path:
        client.connect(
            cfg.host,
            port=cfg.port,
            username=cfg.user,
            key_filename=cfg.key_path,
            timeout=timeout,
        )
    else:
        client.connect(
            cfg.host,
            port=cfg.port,
            username=cfg.user,
            password=cfg.password,
            timeout=timeout,
        )
    return client


def run(client: paramiko.SSHClient, cmd: str, timeout: int = 300) -> str:
    """执行远程命令并打印输出。"""
    print(f">>> {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    if out:
        print(out[-3000:])
    if err:
        print("[STDERR]", err[-1000:])
    return out + err
