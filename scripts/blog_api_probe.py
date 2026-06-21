#!/usr/bin/env python3
"""
探测远程网站是否暴露了常见博客平台的发布 API。

用法：
  python blog_api_probe.py --url https://your-blog.com

依赖：pip install -r requirements.txt
"""
import argparse
import sys

import requests

PROBES = [
    {
        "name": "WordPress REST API",
        "endpoint": "/wp-json/wp/v2/posts",
        "method": "GET",
        "check": lambda r: r.status_code == 200 and "id" in r.text,
    },
    {
        "name": "Ghost Content API",
        "endpoint": "/ghost/api/v3/content/site/?key=demo",
        "method": "GET",
        "check": lambda r: r.status_code in (200, 401) and "ghost" in r.text.lower(),
    },
    {
        "name": "Halo Console API",
        "endpoint": "/apis/api.console.halo.run/v1alpha1/posts",
        "method": "GET",
        "check": lambda r: r.status_code in (200, 401),
    },
]


def probe(base_url: str) -> list:
    results = []
    base = base_url.rstrip("/")
    for p in PROBES:
        url = base + p["endpoint"]
        try:
            resp = requests.request(p["method"], url, timeout=10, allow_redirects=False)
            detected = p["check"](resp)
            results.append(
                {
                    "name": p["name"],
                    "url": url,
                    "status": resp.status_code,
                    "detected": detected,
                }
            )
            print(f"{'[√]' if detected else '[×]'} {p['name']}: {url} (HTTP {resp.status_code})")
        except Exception as e:
            print(f"[×] {p['name']}: {url} ({e})")
            results.append({"name": p["name"], "url": url, "status": None, "detected": False})
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="探测博客发布 API")
    parser.add_argument("--url", required=True, help="博客站点首页地址")
    args = parser.parse_args()

    print(f"正在探测: {args.url}\n")
    results = probe(args.url)

    detected = [r for r in results if r["detected"]]
    if detected:
        print(f"\n检测到 {len(detected)} 个可能的 API：")
        for r in detected:
            print(f"  - {r['name']}: {r['url']}")
    else:
        print("\n未检测到常见博客 API，可能是静态博客或自定义平台。")

    return 0


if __name__ == "__main__":
    sys.exit(main())
