#!/usr/bin/env python3
"""
发布文章到博客平台。

目前支持：
  - WordPress REST API
  - Ghost Admin API

用法：
  python publish_post.py --platform wordpress --file post.md --title "标题" --status draft
  python publish_post.py --platform ghost --file post.md --title "标题"

依赖：pip install -r requirements.txt
"""
import argparse
import os
import re
import sys
from datetime import datetime, timezone

import jwt
import requests


def parse_frontmatter(content: str) -> tuple:
    """解析 Markdown 文件顶部的 YAML frontmatter。"""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            meta = {}
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"').strip("'")
            return meta, parts[2].strip()
    return {}, content.strip()


def publish_wordpress(file_path: str, title: str, status: str = "draft") -> dict:
    api_url = os.getenv("BLOG_API_URL").rstrip("/") + "/wp-json/wp/v2/posts"
    username = os.getenv("BLOG_USERNAME")
    password = os.getenv("BLOG_PASSWORD")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    meta, body = parse_frontmatter(content)
    payload = {
        "title": title or meta.get("title", "Untitled"),
        "content": markdown_to_html(body),
        "status": status,
    }

    resp = requests.post(api_url, json=payload, auth=(username, password), timeout=30)
    resp.raise_for_status()
    return resp.json()


def publish_ghost(file_path: str, title: str, status: str = "draft") -> dict:
    base = os.getenv("BLOG_API_URL").rstrip("/")
    admin_key = os.getenv("BLOG_API_KEY")

    # Ghost Admin API key: <id>:<secret>
    if ":" not in admin_key:
        raise ValueError("Ghost Admin API key 格式应为 <id>:<secret>")

    key_id, secret = admin_key.split(":", 1)

    iat = int(datetime.now(tz=timezone.utc).timestamp())
    token = jwt.encode(
        {"iat": iat, "exp": iat + 300, "aud": "/v3/admin/"},
        bytes.fromhex(secret),
        algorithm="HS256",
        headers={"kid": key_id},
    )

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    meta, body = parse_frontmatter(content)
    # Ghost 状态字段为 published 或 draft
    ghost_status = "published" if status == "publish" else status

    payload = {
        "posts": [
            {
                "title": title or meta.get("title", "Untitled"),
                "html": markdown_to_html(body),
                "status": ghost_status,
            }
        ]
    }

    headers = {"Authorization": f"Ghost {token}"}
    resp = requests.post(f"{base}/ghost/api/v3/admin/posts/", json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def markdown_to_html(md: str) -> str:
    """极简 Markdown 转 HTML，仅处理标题和换行。"""
    html = re.sub(r"^### (.*)$", r"<h3>\1</h3>", md, flags=re.M)
    html = re.sub(r"^## (.*)$", r"<h2>\1</h2>", html, flags=re.M)
    html = re.sub(r"^# (.*)$", r"<h1>\1</h1>", html, flags=re.M)
    html = "\n".join(f"<p>{line}</p>" for line in html.split("\n\n") if line.strip())
    return html


PLATFORMS = {
    "wordpress": publish_wordpress,
    "ghost": publish_ghost,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="发布文章到博客平台")
    parser.add_argument("--platform", choices=list(PLATFORMS.keys()), required=True)
    parser.add_argument("--file", required=True, help="Markdown 文件路径")
    parser.add_argument("--title", default="", help="文章标题（默认读取 frontmatter 或文件名）")
    parser.add_argument("--status", default="draft", help="文章状态：draft/publish")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"文件不存在: {args.file}")
        return 1

    if not os.getenv("BLOG_API_URL"):
        print("请先在 .env 中配置 BLOG_API_URL")
        return 1

    try:
        result = PLATFORMS[args.platform](args.file, args.title, args.status)
        print("发布成功:")
        print(result)
    except Exception as e:
        print(f"发布失败: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
