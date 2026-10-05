<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 009 · Container lifecycle · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

A container's main process fails at once with exit code 1. Start it with the restart policy `--restart on-failure:3`, so
that Docker restarts it at most three times, and show how many restarts Docker made.

## Solution

```bash
docker run -d --name flaky --restart on-failure:3 alpine:3.23 sh -c 'echo starting; exit 1'
```

Wait a few seconds, then:

```bash
docker inspect --format 'restarts: {{.RestartCount}}, status: {{.State.Status}}, exit code: {{.State.ExitCode}}' flaky
```

```text
restarts: 3, status: exited, exit code: 1
```

Docker restarted it three times (waiting a little longer each time), then gave up: the container stays `exited` with
code 1. `docker logs flaky` shows `starting` four times. Other policies: `no` (default), `always`, `unless-stopped`
(lesson 131).
