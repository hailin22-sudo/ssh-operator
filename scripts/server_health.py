#!/usr/bin/env python3
"""
远程服务器健康检查脚本。

用法：
  python server_health.py [--url http://<IP>:<PORT>/api/v1/health]

依赖：pip install -r requirements.txt
"""
import argparse
import sys

import requests

from _ssh import connect, load_config, run

CHECKS = [
    ("系统负载", "uptime"),
    ("内存使用", "free -h"),
    ("磁盘使用", "df -h /"),
    ("Docker 容器", 'docker ps --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"'),
    ("Nginx 进程数", "pgrep -c nginx || echo 0"),
]


def check_http(url: str, timeout: int = 10) -> dict:
    try:
        resp = requests.get(url, timeout=timeout)
        return {
            "url": url,
            "status": resp.status_code,
            "ok": resp.status_code < 400,
            "body": resp.text[:200],
        }
    except Exception as e:
        return {"url": url, "status": None, "ok": False, "body": str(e)}


def main() -> int:
    parser = argparse.ArgumentParser(description="远程服务器健康检查")
    parser.add_argument("--url", help="HTTP 健康检查地址", default="")
    args = parser.parse_args()

    cfg = load_config()
    client = connect(cfg)

    try:
        print(f"=== 服务器健康检查: {cfg.host}:{cfg.port} ===\n")
        for name, cmd in CHECKS:
            print(f"--- {name} ---")
            run(client, cmd, timeout=60)
            print()
    finally:
        client.close()

    if args.url:
        print("--- HTTP 健康检查 ---")
        result = check_http(args.url)
        print(f"URL: {result['url']}")
        print(f"状态: {result['status']}")
        print(f"结果: {'通过' if result['ok'] else '失败'}")
        print(f"响应: {result['body']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
