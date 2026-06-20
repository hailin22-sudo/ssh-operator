#!/usr/bin/env python3
"""
远程日志收集脚本。

用法：
  python log_collector.py --service backend --lines 500
  python log_collector.py --nginx
  python log_collector.py --service backend --nginx --baota

依赖：pip install -r requirements.txt
"""
import argparse
import os
import sys
from datetime import datetime

from _ssh import connect, load_config, run


def collect_docker_logs(cfg, service: str, lines: int, output_dir: str) -> str:
    client = connect(cfg)
    try:
        filename = f"docker-{service}-{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
        local_path = os.path.join(output_dir, filename)
        os.makedirs(output_dir, exist_ok=True)

        stdin, stdout, stderr = client.exec_command(
            f"cd {cfg.remote_root} && docker-compose logs --tail={lines} {service}"
        )
        logs = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")

        with open(local_path, "w", encoding="utf-8") as f:
            f.write(logs)
            if err:
                f.write("\n[STDERR]\n" + err)

        return local_path
    finally:
        client.close()


def collect_nginx_logs(cfg, output_dir: str) -> str:
    client = connect(cfg)
    try:
        filename = f"nginx-error-{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
        local_path = os.path.join(output_dir, filename)
        os.makedirs(output_dir, exist_ok=True)

        sftp = client.open_sftp()
        try:
            sftp.get("/www/wwwlogs/nginx-error.log", local_path)
        except FileNotFoundError:
            with open(local_path, "w", encoding="utf-8") as f:
                f.write("未找到 /www/wwwlogs/nginx-error.log")
        finally:
            sftp.close()

        return local_path
    finally:
        client.close()


def collect_baota_logs(cfg, output_dir: str) -> str:
    client = connect(cfg)
    try:
        filename = f"baota-{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
        local_path = os.path.join(output_dir, filename)
        os.makedirs(output_dir, exist_ok=True)

        stdin, stdout, stderr = client.exec_command("tail -n 300 /www/server/panel/logs/error.log")
        logs = stdout.read().decode("utf-8", errors="replace")

        with open(local_path, "w", encoding="utf-8") as f:
            f.write(logs)

        return local_path
    finally:
        client.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="远程日志收集")
    parser.add_argument("--service", help="Docker Compose 服务名")
    parser.add_argument("--lines", type=int, default=300, help="Docker 日志行数")
    parser.add_argument("--nginx", action="store_true", help="收集 Nginx 错误日志")
    parser.add_argument("--baota", action="store_true", help="收集宝塔面板日志")
    args = parser.parse_args()

    if not args.service and not args.nginx and not args.baota:
        parser.print_help()
        return 1

    cfg = load_config()
    output_dir = cfg.local_log_dir
    results = []

    if args.service:
        results.append(collect_docker_logs(cfg, args.service, args.lines, output_dir))
    if args.nginx:
        results.append(collect_nginx_logs(cfg, output_dir))
    if args.baota:
        results.append(collect_baota_logs(cfg, output_dir))

    print("日志已保存到：")
    for r in results:
        print("  ", r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
