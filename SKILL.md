---
name: "ssh-operator"
description: "Connects to remote servers via SSH/SFTP to deploy multi-file projects, manage Docker services, and inspect logs. Invoke when the user asks for anything involving remote servers, deployment, SSH operations, or Baota panel hosting."
license: "MIT"
compatibility: "Requires SSH/SFTP access, paramiko (Python) or OpenSSH client, and Docker on the remote host. Works with Claude Code, Codex, TRAE, and other Agent-Skills-compatible platforms."
metadata:
  author: "zhu-hailin"
  version: "1.0.0"
  keywords:
    - "ssh"
    - "sftp"
    - "deployment"
    - "docker"
    - "baota"
    - "宝塔"
    - "ai-agent"
    - "agent-skill"
    - "claude-code"
    - "trae"
    - "codex"
    - "cursor"
    - "blog-publishing"
    - "nginx"
  categories:
    - "DevOps"
    - "Deployment"
    - "Server Management"
---

# SSH Operator

Operate remote Linux servers over SSH/SFTP to deploy applications, manage Docker containers, and inspect runtime state. Supports multi-file / multi-folder projects and is adapted for Baota (宝塔) panel environments.

## When to invoke

- The user asks to deploy, publish, or release code to a server.
- The user asks to restart, rebuild, or update a remote service.
- The user asks to upload files or entire folders to a remote host.
- The user asks to view remote logs or check service status.
- The user asks to run commands or diagnose issues on a remote server.
- The user asks to edit remote website/blog source files.
- The user asks to publish a blog post or detect a blog platform's publishing API.
- The user mentions Baota / 宝塔 panel, `/www/wwwroot/`, or Chinese cloud VPS hosting.

## Capabilities

- Connect to remote hosts over SSH (password or key-based auth).
- Upload/download files and recursively upload folders via SFTP.
- Execute shell commands and stream output.
- Manage Docker and docker-compose workloads.
- Inspect service health, logs, disk usage, and process state.
- Validate that deployed changes are active (checksums, process restarts, HTTP health checks).
- Adapt commands for Baota panel directory layout and Nginx reverse-proxy setups.
- Edit remote website/blog source files directly over SSH.
- Detect blog publishing APIs (WordPress, Ghost, Halo) and publish Markdown posts via Python scripts.

## Required inputs

Collect these from the user or environment before acting:

1. `HOST` — server IP or hostname.
2. `PORT` — SSH port (default 22).
3. `USER` — SSH username.
4. `AUTH` — password or private-key path. Prefer keys; never hard-code secrets in committed files.
5. `REMOTE_ROOT` — base project path on the server (e.g. `/www/wwwroot/ai-interviewer`).
6. `FILES_TO_UPLOAD` — list of `local_path -> remote_relative_path` pairs, including entire folders.
7. `COMMANDS` — the deployment or diagnostic commands to run.

## Multi-file / multi-folder deployment

Most real projects are not a single file. Use one of these approaches:

### Option 1: Use the provided script template

Copy [`scripts/deploy-folder.py`](scripts/deploy-folder.py) into the project repo, configure the `FILES_TO_UPLOAD` list, and run it. It handles recursive folder uploads and preserves relative paths.

For Unix-like local environments, [`scripts/deploy-rsync.sh`](scripts/deploy-rsync.sh) provides an incremental rsync-based alternative with sensible excludes.

### Option 2: Agent-driven SFTP

When the agent has SFTP/SSH tools:

1. Establish the SSH session.
2. For each changed folder, walk its contents and upload files individually, recreating the remote directory tree.
3. For each changed file, upload to the matching remote relative path.
4. Run deployment commands and verify.

### Option 3: One-shot tarball

For large projects, prefer packing locally and extracting remotely:

```bash
# Local
 tar czf deploy.tar.gz backend/app frontend/.next docker-compose.yml .env.production
 scp deploy.tar.gz user@host:/tmp/

# Remote
 ssh user@host "cd /www/wwwroot/project && tar xzf /tmp/deploy.tar.gz && docker-compose up -d --build"
```
## Script library

Ready-to-use automation scripts. Python scripts share [`scripts/_ssh.py`](scripts/_ssh.py) for connection/config loading and read credentials from a `.env` file (see `.env.example`). Copy the script together with `_ssh.py` into your project.

| Script | Purpose |
|---|---|
| [`scripts/_ssh.py`](scripts/_ssh.py) | Shared helper: load `.env` config and open an SSH/SFTP connection. |
| [`scripts/deploy-folder.py`](scripts/deploy-folder.py) | Recursive SFTP upload of files and folders, then run post-deploy commands. |
| [`scripts/deploy-rsync.sh`](scripts/deploy-rsync.sh) | Incremental rsync deploy with common excludes. |
| [`scripts/blog_api_probe.py`](scripts/blog_api_probe.py) | Detect common blog publishing APIs (WordPress, Ghost, Halo). |
| [`scripts/publish_post.py`](scripts/publish_post.py) | Publish a Markdown file to WordPress or Ghost via REST API. |
| [`scripts/backup_before_deploy.py`](scripts/backup_before_deploy.py) | Backup code, Nginx configs, Docker volumes, and SQLite before deploying. |
| [`scripts/server_health.py`](scripts/server_health.py) | Collect CPU, memory, disk, Docker, Nginx, and HTTP health status. |
| [`scripts/log_collector.py`](scripts/log_collector.py) | Pull Docker, Nginx, and Baota logs to local files for analysis. |
| [`scripts/nginx_manager.py`](scripts/nginx_manager.py) | Read/backup/edit Baota Nginx site configs and reload safely. |
| [`scripts/bt_panel.py`](scripts/bt_panel.py) | Install Baota, view panel info, reload Nginx, and check Docker status over SSH. |

Python dependencies are listed in [`requirements.txt`](requirements.txt).

## Standard deployment workflow

1. **Establish the SSH session** with the provided credentials and a reasonable timeout (≥20 s).
2. **Backup before changing anything** — run [`scripts/backup_before_deploy.py`](scripts/backup_before_deploy.py) or equivalent.
3. **Ensure `REMOTE_ROOT` exists** (`mkdir -p`).
4. **Upload files/folders** preserving relative paths under `REMOTE_ROOT`.
5. **Run commands** in order; prefer chaining dependent commands with `&&`.
6. **Wait for services** to start (use `sleep` + `docker-compose ps` or a health endpoint).
7. **Verify** the new code is live (grep inside the container, hit `/health`, check logs).
8. **Report outcomes** concisely: what changed, whether services are healthy, and any errors.

## Common command patterns

```bash
# Stop, rebuild, and restart a service
cd ${REMOTE_ROOT} && docker-compose stop backend \
  && docker-compose rm -f backend \
  && docker-compose build backend \
  && docker-compose up -d backend

# Check service status
cd ${REMOTE_ROOT} && docker-compose ps

# View recent logs
cd ${REMOTE_ROOT} && docker-compose logs --tail=50 backend

# Verify code inside the running container
docker exec ${CONTAINER_NAME} grep -n "await db.flush()" app/api/v1/interview.py

# Disk cleanup
docker system prune -a -f
```

## Baota / 宝塔 panel adaptation

See [`references/baota.md`](references/baota.md) for the full operational guide and [`references/bt-commands.md`](references/bt-commands.md) for the `bt` CLI cheat sheet. Key points:

- Official site: https://www.bt.cn; install script at https://www.bt.cn/new/download.html.
- Default project root: `/www/wwwroot/<site-name>`.
- Use [`scripts/bt_panel.py`](scripts/bt_panel.py) to install Baota, view panel info, or reload Nginx over SSH.
- Use Docker Compose inside the project directory; manage containers via CLI or the Baota Docker plugin.
- For Node/Python frontends, add a Baota site and use [`scripts/nginx_manager.py`](scripts/nginx_manager.py) to add Nginx reverse-proxy locations to `127.0.0.1:3000`.
- Route `/api/` to the backend container (e.g. `127.0.0.1:8000`) in Nginx.
- Open ports in both the Baota firewall and the cloud-provider security group.
- Do not expose high-numbered ports directly to the internet; use Nginx on 80/443.

If something goes wrong, consult [`references/troubleshooting.md`](references/troubleshooting.md).

## Safety rules

- **Never commit secrets**. Store `PASS` or key paths in environment variables, `.env` files excluded from git, or a secrets manager.
- **Prefer explicit file lists** over broad uploads to avoid overwriting unexpected files.
- **Run non-destructive checks first** when diagnosing (logs, ps, df) before restarting services.
- **Avoid `git push --force` or destructive `rm -rf`** unless the user explicitly requests it.
- **Confirm risky actions** (database migrations, service-wide restarts, destructive deletes) with the user when possible.
- **Clean up temporary files** (e.g. `/tmp/deploy.tar.gz`) after deployment.

## Cross-platform notes

- This skill assumes a Linux remote host and a local environment with an SSH client or a Python library such as `paramiko`.
- On Windows local hosts, paths may need normalization; always quote remote paths in commands.
- On agents without direct SSH tools, fall back to: (1) generating a deployment script for the user to run, or (2) using the platform's provided terminal/remote execution tool.
- For maximum portability across Claude Code, Codex, TRAE, and Cursor, keep the main `SKILL.md` under 500 lines and move detailed references into `references/`.

## Example

User: "Deploy the latest backend fix to my Baota server."

Agent:
1. Ask for or load `HOST`, `PORT`, `USER`, auth, and `REMOTE_ROOT`.
2. Ask which files changed, or infer from recent edits.
3. Upload the changed files/folders to their remote paths under `REMOTE_ROOT`.
4. Rebuild and restart the affected Docker service(s).
5. Check `docker-compose ps` and tail logs to confirm health.
6. Reply with a short summary of uploads and service status.
