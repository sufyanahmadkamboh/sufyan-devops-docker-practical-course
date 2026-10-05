<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 084 · Read-only file systems · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Start nginx read-only:

```bash
docker run -d --name web-ro --read-only -p 8080:80 nginx:1.30-alpine > /dev/null && echo "started web-ro"
```

```bash
docker ps -a --filter name=web-ro --format '{{.Names}}: {{.Status}}'
```

## Troubleshoot it

The container stopped almost immediately. The last log lines explain it:

```bash
docker logs web-ro 2>&1 | tail -2
```

```text
2026/10/05 16:57:12 [emerg] 1#1: mkdir() "/var/cache/nginx/client_temp" failed (30: Read-only file system)
nginx: [emerg] mkdir() "/var/cache/nginx/client_temp" failed (30: Read-only file system)
```

`mkdir() "/var/cache/nginx/client_temp" failed (30: Read-only file system)`: nginx needs a few writable folders for
temporary files and its PID file. `docker diff` in the lab showed which. This is the normal process for any image: run
it once writable, list what it writes, and decide for each folder: tmpfs (scratch) or a volume (data to keep).

## Fix it

Give nginx the two writable folders it needs as tmpfs mounts; everything else stays read-only:

```bash
docker rm -f web-ro > /dev/null
docker run -d --name web-ro --read-only --tmpfs /var/cache/nginx --tmpfs /run -p 8080:80 nginx:1.30-alpine > /dev/null && echo "started web-ro"
```

```bash
curl -s http://localhost:8080/ | grep -o '<title>.*</title>'
```

```bash
docker exec web-ro sh -c 'echo hacked > /usr/share/nginx/html/index.html' 2>&1 || true
```

```text
sh: can't create /usr/share/nginx/html/index.html: Read-only file system
```

nginx serves its page, and the page cannot be replaced from inside the container.
