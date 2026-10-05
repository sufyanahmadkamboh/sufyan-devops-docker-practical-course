<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 131 · Container design · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A (hypothetical) worker written the "server way": it writes its log to a file inside the container.

```bash
docker run -d --name worker alpine:3.23 sh -c 'while true; do echo "$(date +%T) order processed" >> /var/log/app.log; sleep 1; done' > /dev/null
sleep 3
docker logs worker
echo "lines in docker logs: $(docker logs worker 2>&1 | wc -l | tr -d ' ')"
```

```text
lines in docker logs: 0
```

`docker logs worker` prints nothing: zero lines, although the worker has been working for three seconds.

## Troubleshoot it

The container is running and working: the log exists, but only inside the container's file system:

```bash
docker exec worker tail -n 2 /var/log/app.log
```

```text
12:16:44 order processed
12:16:45 order processed
```

Docker (and Kubernetes, and every log collector built on them) only captures a container's **standard output and
error**. A file inside the container is invisible to them, it fills the container's writable layer, and it disappears
with the container (lesson 053). In production, nobody would see this worker's logs.

## Fix it

Write to standard output. When you can change the application, print instead of writing a file; when you cannot, do
what the Nginx image does and point the log file at `/dev/stdout`:

```bash
docker rm -f worker > /dev/null
docker run -d --name worker alpine:3.23 sh -c 'ln -sf /dev/stdout /var/log/app.log; while true; do echo "$(date +%T) order processed" >> /var/log/app.log; sleep 1; done'
sleep 3
docker logs worker | tail -n 2
```
