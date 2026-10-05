<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 014 · Container logs · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

An application writes its log to a file instead of stdout:

```bash
docker run -d --name filelogger alpine:3.23 sh -c 'while true; do echo "$(date) heartbeat" >> /var/log/app.log; sleep 1; done' > /dev/null
sleep 2
echo "log lines: $(docker logs filelogger 2>&1 | wc -l | tr -d ' ')"
```

```text
log lines: 0
```

## Troubleshoot it

The container is running, but `docker logs` is empty. Docker only sees stdout and stderr of the main process. Look
inside the container (`docker exec` runs a command in a running container, lesson 015):

```bash
docker exec filelogger tail -2 /var/log/app.log
```

```text
Mon Oct  5 10:49:07 UTC 2026 heartbeat
Mon Oct  5 10:49:08 UTC 2026 heartbeat
```

The log exists, in a file Docker does not read. It also grows inside the container's writable layer until the disk is
full, and disappears when the container is removed.

## Fix it

Write to stdout. When you cannot change the application, do what the Nginx image does: make the log file a link to
the container's stdout:

```bash
docker run --rm nginx:1.30-alpine ls -l /var/log/nginx/
```

```text
total 0
lrwxrwxrwx    1 root     root            11 Sep 22 21:19 access.log -> /dev/stdout
lrwxrwxrwx    1 root     root            11 Sep 22 21:19 error.log -> /dev/stderr
```

For our application, the fix is to print instead of appending to a file:

```bash
docker rm -f filelogger > /dev/null
docker run -d --name filelogger alpine:3.23 sh -c 'while true; do echo "$(date) heartbeat"; sleep 1; done' > /dev/null 2>&1 || true
sleep 2
docker logs --tail 1 filelogger
```
