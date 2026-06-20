#!/usr/bin/env python3
"""
宝塔面板（Baota）SSH 操作脚本。

不依赖宝塔 API Key，直接通过 SSH 在服务器上执行 `bt` 命令。

用法：
  python bt_panel.py <action>

依赖：pip install -r requirements.txt
"""
import sys

from _ssh import connect, load_config, run

# 宝塔官方安装脚本（来自 https://www.bt.cn/new/download.html）
BT_INSTALL_CMD = (
    "if [ -f /usr/bin/curl ];then curl -sSO https://download.bt.cn/install/install_panel.sh;"
    "else wget -O install_panel.sh https://download.bt.cn/install/install_panel.sh;fi;"
    "bash install_panel.sh ed8484bec"
)


def install(cfg):
    print("开始安装宝塔面板，请耐心等待...")
    client = connect(cfg, timeout=600)
    try:
        run(client, BT_INSTALL_CMD, timeout=600)
        run(client, "bt default")
    finally:
        client.close()


def info(cfg):
    client = connect(cfg)
    try:
        run(client, "bt default")
    finally:
        client.close()


def restart(cfg):
    client = connect(cfg)
    try:
        run(client, "bt restart")
    finally:
        client.close()


def reload_nginx(cfg):
    client = connect(cfg)
    try:
        run(client, "bt reload nginx")
    finally:
        client.close()


def panel_port(cfg):
    client = connect(cfg)
    try:
        run(client, "cat /www/server/panel/data/port.pl")
    finally:
        client.close()


def docker_status(cfg):
    client = connect(cfg)
    try:
        run(client, 'docker ps --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"')
    finally:
        client.close()


ACTIONS = {
    "install": install,
    "info": info,
    "restart": restart,
    "reload-nginx": reload_nginx,
    "panel-port": panel_port,
    "docker-status": docker_status,
}


def main() -> int:
    if len(sys.argv) < 2:
        print("用法：python bt_panel.py <action>")
        print("可用 action:", ", ".join(ACTIONS.keys()))
        return 1

    action = sys.argv[1]
    if action not in ACTIONS:
        print(f"未知 action: {action}")
        print("可用 action:", ", ".join(ACTIONS.keys()))
        return 1

    cfg = load_config()
    ACTIONS[action](cfg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
