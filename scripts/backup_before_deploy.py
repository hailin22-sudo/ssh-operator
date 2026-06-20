#!/usr/bin/env python3
"""
部署前自动备份脚本。

用法：
  python backup_before_deploy.py --db-path /www/wwwroot/your-project/data/app.db

会在服务器端创建备份目录 /www/backup/<日期>/，包含：
  - 项目代码压缩包
  - Nginx 站点配置压缩包
  - Docker volumes 备份
  - SQLite 数据库副本

依赖：pip install -r requirements.txt
"""
import argparse
import sys
from datetime import datetime

from _ssh import connect, load_config, run


def main() -> int:
    parser = argparse.ArgumentParser(description="部署前自动备份")
    parser.add_argument("--db-path", help="SQLite 数据库路径（可选）", default="")
    parser.add_argument(
        "--volumes",
        nargs="*",
        default=["data", "uploads"],
        help="要备份的 Docker volume/数据目录（相对 REMOTE_ROOT）",
    )
    args = parser.parse_args()

    cfg = load_config()
    client = connect(cfg)

    try:
        date_str = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_dir = f"{cfg.backup_dir}/{date_str}"

        run(client, f"mkdir -p {backup_dir}")

        # 1. 备份项目代码
        run(
            client,
            f"cd /www/wwwroot && tar czf {backup_dir}/project.tar.gz {cfg.remote_root.split('/')[-1]}",
        )

        # 2. 备份 Nginx 配置
        run(
            client,
            f"tar czf {backup_dir}/nginx.tar.gz -C /www/server/panel/vhost nginx",
        )

        # 3. 备份 Docker volumes/数据目录
        for vol in args.volumes:
            run(
                client,
                f"cd {cfg.remote_root} && tar czf {backup_dir}/{vol}.tar.gz {vol}",
            )

        # 4. 备份 SQLite 数据库
        if args.db_path:
            run(client, f"cp {args.db_path} {backup_dir}/app.db.bak")

        print(f"\n备份完成: {backup_dir}")
        run(client, f"ls -lh {backup_dir}")
    finally:
        client.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
