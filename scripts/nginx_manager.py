#!/usr/bin/env python3
"""
宝塔 Nginx 配置管理脚本。

用法：
  python nginx_manager.py show --site example.com
  python nginx_manager.py add-proxy --site example.com --path /api/ --target http://127.0.0.1:8000/
  python nginx_manager.py reload

依赖：pip install -r requirements.txt
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

from _ssh import connect, load_config, run

NGINX_CONF_DIR = "/www/server/panel/vhost/nginx"


def show_config(cfg, site: str) -> None:
    client = connect(cfg)
    try:
        run(client, f"cat {NGINX_CONF_DIR}/{site}.conf")
    finally:
        client.close()


def backup_config(cfg, site: str) -> str:
    client = connect(cfg)
    try:
        path = f"{NGINX_CONF_DIR}/{site}.conf"
        backup_path = f"{path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        run(client, f"cp {path} {backup_path}")
        return backup_path
    finally:
        client.close()


def add_proxy_location(cfg, site: str, path: str, target: str) -> None:
    """在站点配置文件中追加一个 location 反代块。"""
    conf_path = f"{NGINX_CONF_DIR}/{site}.conf"

    location_block = f"""
    location {path} {{
        proxy_pass {target};
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
"""

    client = connect(cfg)
    try:
        # 先备份
        backup_path = f"{conf_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        run(client, f"cp {conf_path} {backup_path}")

        # 使用 printf 安全追加，避免引号转义问题
        escaped = location_block.replace("'", "'\\''")
        cmd = f"printf '%s' '{escaped}' >> {conf_path}"
        run(client, cmd)

        print(f"已追加反代配置: {path} -> {target}")
        run(client, "nginx -t")
    finally:
        client.close()


def reload_nginx(cfg) -> None:
    client = connect(cfg)
    try:
        run(client, "bt reload nginx")
    finally:
        client.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="宝塔 Nginx 配置管理")
    sub = parser.add_subparsers(dest="action", required=True)

    p_show = sub.add_parser("show", help="查看站点 Nginx 配置")
    p_show.add_argument("--site", required=True)

    sub.add_parser("backup", help="备份站点 Nginx 配置").add_argument("--site", required=True)

    p_proxy = sub.add_parser("add-proxy", help="追加反向代理 location")
    p_proxy.add_argument("--site", required=True)
    p_proxy.add_argument("--path", required=True)
    p_proxy.add_argument("--target", required=True)

    sub.add_parser("reload", help="重载 Nginx")

    args = parser.parse_args()
    cfg = load_config()

    if args.action == "show":
        show_config(cfg, args.site)
    elif args.action == "backup":
        backup_config(cfg, args.site)
    elif args.action == "add-proxy":
        add_proxy_location(cfg, args.site, args.path, args.target)
    elif args.action == "reload":
        reload_nginx(cfg)

    return 0


if __name__ == "__main__":
    sys.exit(main())
