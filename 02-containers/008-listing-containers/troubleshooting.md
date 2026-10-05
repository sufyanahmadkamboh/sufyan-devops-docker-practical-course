<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 008 · Listing containers · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

You remember that stopped containers are "stopped", so you filter on that:

```bash
docker ps -a --filter status=stopped
```

```text
Error response from daemon: invalid filter 'status=stopped': invalid value for state (stopped): must be one of created, running, paused, restarting, removing, exited, dead
```

## Troubleshoot it

`invalid value for state (stopped): must be one of created, running, paused, restarting, removing, exited, dead`. The
error lists every valid value: Docker calls a stopped container **exited**. Filter keys and values are fixed words,
listed in `docker ps --help` and in the error itself. Read the whole error line before searching the web.

## Fix it

```bash
docker ps -a --filter status=exited --format '{{.Names}}: {{.Status}}'
```
