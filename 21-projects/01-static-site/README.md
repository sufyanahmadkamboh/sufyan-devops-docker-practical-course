# Project 01 · Static website on Nginx

> ⏱ 45 minutes · run every command from the course folder

## Goal

Ship the cafe's static website ([examples/site](../../examples/site)) as a production-ready Nginx image: your own
Nginx configuration, no root user, a healthcheck, and a container that also runs with a read-only file system.

## Requirements

- [ ] The image is built from `nginx:1.30-alpine` with the site and a custom `nginx.conf` inside it
- [ ] Nginx listens on port 8080 and runs as the `nginx` user, not root
- [ ] `/healthz` answers `ok`, and Docker reports the container **healthy**
- [ ] Responses carry `X-Content-Type-Options` and `X-Frame-Options` headers, and no Nginx version
- [ ] The container runs with `--read-only` (only `/tmp` writable)

## Architecture

```text
 browser ──▶ localhost:8080 ──▶ ┌─────────────────────────────────┐
                                │ container cafe-site             │
                                │ nginx (user nginx), port 8080   │
                                │ /usr/share/nginx/html (image)   │
                                │ /tmp  ◀── tmpfs (only writable) │
                                └─────────────────────────────────┘
```

## Build it

Create the lab: the site plus the solution files (try writing your own `Dockerfile` and `nginx.conf` first, then
compare):

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh project-01 examples/site
cp -r 21-projects/01-static-site/solution/. ~/docker-practice/project-01/
cd ~/docker-practice/project-01
ls -A
```

The Dockerfile:

<!-- test: contains=USER nginx; output -->
```bash
cat Dockerfile
```

```text
# A static site on Nginx: custom configuration, non-root, with a healthcheck.
FROM nginx:1.30-alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY index.html styles.css /usr/share/nginx/html/
USER nginx
EXPOSE 8080
HEALTHCHECK --interval=5s --timeout=3s --retries=3 CMD ["wget", "-q", "-O", "/dev/null", "http://127.0.0.1:8080/healthz"]
```

The Nginx configuration moves every file Nginx writes (its PID file and temporary folders) to `/tmp`, so it can run as
a normal user and on a read-only file system:

<!-- test: contains=pid /tmp/nginx.pid -->
```bash
grep -E "pid|listen|temp_path" nginx.conf
```

Check the configuration with Nginx itself before building, then build:

<!-- test: contains=syntax is ok -->
```bash
docker run --rm -v "$(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro" nginx:1.30-alpine nginx -t 2>&1
```

<!-- test: contains=cafe-site -->
```bash
docker build -q -t cafe-site:1.0 . > /dev/null
docker image ls --format '{{.Repository}}:{{.Tag}} {{.Size}}' cafe-site
```

Run it with a read-only root file system and a small in-memory `/tmp`:

<!-- test -->
```bash
docker run -d --name cafe-site -p 8080:8080 --read-only --tmpfs /tmp cafe-site:1.0 > /dev/null
```

## Verify

The page, and the security headers:

<!-- test: contains=Welcome to the cafe; retry=10 -->
```bash
curl -s http://localhost:8080/ | grep "<h1>"
```

<!-- test: contains=X-Frame-Options: DENY; absent=nginx/1; output -->
```bash
curl -sI http://localhost:8080/ | grep -iE "^(server|x-content-type-options|x-frame-options):"
```

```text
Server: nginx
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
```

`Server: nginx` without a version: `server_tokens off` hides it. The user, and the health status:

<!-- test: contains=uid=101(nginx); output -->
```bash
docker exec cafe-site id
```

```text
uid=101(nginx) gid=101(nginx) groups=101(nginx)
```

<!-- test: contains=healthy; retry=15 -->
```bash
docker inspect --format '{{.State.Health.Status}}' cafe-site
```

The read-only file system holds:

<!-- test: contains=Read-only file system -->
```bash
docker exec cafe-site sh -c 'echo defaced > /usr/share/nginx/html/index.html' 2>&1 || true
```

## Break it and fix it

Run the same image read-only, but forget the writable `/tmp`:

<!-- test: contains=Read-only file system; output -->
```bash
docker run -d --name cafe-site-broken -p 8081:8080 --read-only cafe-site:1.0 > /dev/null
sleep 2
docker ps -a --filter name=cafe-site-broken --format '{{.Names}}: {{.Status}}'
docker logs cafe-site-broken 2>&1 | grep -m1 emerg
```

```text
cafe-site-broken: Exited (1) 2 seconds ago
2026/10/05 12:25:55 [emerg] 1#1: mkdir() "/tmp/client_temp" failed (30: Read-only file system)
```

Nginx exits at once: `Read-only file system` on a path under `/tmp`. With `--read-only`, **every** path is read-only,
including the folders the configuration moved to `/tmp`. The fix is to give the container exactly the writable space
it needs, in memory:

<!-- test: contains=Welcome to the cafe; retry=10 -->
```bash
docker rm -f cafe-site-broken > /dev/null
docker run -d --name cafe-site-broken -p 8081:8080 --read-only --tmpfs /tmp cafe-site:1.0 > /dev/null
curl -s http://localhost:8081/ | grep "<h1>"
```

## Stretch goals

- Add a `Cache-Control` header for `styles.css` and check it with `curl -sI`.
- Add `--cap-drop ALL --security-opt no-new-privileges` to the `docker run` and prove it still works (lesson 085).
- Write a `compose.yaml` that runs the same container with the same options (module 10).

## Cleanup

<!-- test -->
```bash
docker rm -f cafe-site cafe-site-broken > /dev/null
docker image rm -f cafe-site:1.0 > /dev/null
cd ~ && rm -rf ~/docker-practice/project-01
```

Next: [Project 02 · Production Node.js API](../02-node-api/README.md)
