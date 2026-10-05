<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 134 · Security review · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

The first hardening attempt (`broken/compose.yaml`) makes the proxy's file system read-only. Start it:

```bash
cd ~/docker-practice/lesson-134
cp broken/compose.yaml after/compose.broken.yaml
docker compose -p review -f after/compose.broken.yaml up -d --build --wait 2>&1 | tail -3 || true
docker compose -p review -f after/compose.broken.yaml ps -a --format '{{.Service}}: {{.State}}'
```

The API and the database are fine; `web` has exited.

## Troubleshoot it

```bash
docker compose -p review -f after/compose.broken.yaml logs web 2>&1 | grep -i "read-only" | tail -2
```

```text
web-1  | 2026/10/05 12:17:47 [emerg] 1#1: mkdir() "/var/cache/nginx/client_temp" failed (30: Read-only file system)
web-1  | nginx: [emerg] mkdir() "/var/cache/nginx/client_temp" failed (30: Read-only file system)
```

Nginx creates temporary directories under `/var/cache/nginx` (for proxied responses) and writes its PID file under
`/run` at startup. With `read_only: true`, every write fails, so Nginx exits. Hardening is right; it just has to
leave writable space where the application really needs it, and nowhere else.

## Fix it

`after/compose.yaml` adds a `tmpfs` (an in-memory, temporary directory) for exactly those two paths:

```bash
cd ~/docker-practice/lesson-134
docker compose -p review -f after/compose.broken.yaml down -v > /dev/null 2>&1
grep -A3 "tmpfs" after/compose.yaml
docker compose -p review -f after/compose.yaml up -d --wait > /dev/null 2>&1
docker compose -p review -f after/compose.yaml ps --format '{{.Service}}: {{.State}} {{.Health}}'
curl -s http://localhost:8080/ && echo
```

The file system stays read-only everywhere else:

```bash
cd ~/docker-practice/lesson-134
docker compose -p review -f after/compose.yaml exec web sh -c 'touch /etc/nginx/hacked' 2>&1 || true
```
