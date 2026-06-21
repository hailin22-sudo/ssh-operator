# 博客平台 API 速查

本 Skill 支持自动探测并发布文章到常见博客平台。

## 已支持平台

### WordPress

- API 地址：`https://your-blog.com/wp-json/wp/v2/posts`
- 认证：Basic Auth（用户名 + 应用密码）
- 配置：
  ```env
  BLOG_API_URL=https://your-blog.com
  BLOG_USERNAME=admin
  BLOG_PASSWORD=应用密码
  ```
- 发布：
  ```bash
  python scripts/publish_post.py --platform wordpress --file post.md --title "标题" --status publish
  ```

### Ghost

- API 地址：`https://your-blog.com/ghost/api/v3/admin/posts/`
- 认证：Admin API Key（格式 `<id>:<secret>`）
- 配置：
  ```env
  BLOG_API_URL=https://your-blog.com
  BLOG_API_KEY=your-key-id:your-secret
  ```
- 发布：
  ```bash
  python scripts/publish_post.py --platform ghost --file post.md --title "标题" --status publish
  ```

## 自动探测

```bash
python scripts/blog_api_probe.py --url https://your-blog.com
```

会尝试检测 WordPress、Ghost、Halo 等常见博客 API。

## 静态博客

如果你的博客是 Hexo、Hugo、Astro 等静态站点，没有 API，发布方式通常是：

1. 本地写 Markdown 文件
2. 推送到 Git 仓库触发 CI/CD
3. 或上传到服务器（用 `scripts/deploy-folder.py`）

这种情况可以让 Agent 直接修改远程服务器上的 Markdown 源文件，然后执行构建命令。
