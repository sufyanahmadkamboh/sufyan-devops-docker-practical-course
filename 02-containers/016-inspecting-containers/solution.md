<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 016 · Inspecting containers · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Write a one-line "container report" for every container on the engine (running or not): name, image, status, exit code
and restart count, using one `docker inspect` call.

## Solution

```bash
docker inspect --format '{{.Name}} | {{.Config.Image}} | {{.State.Status}} | exit {{.State.ExitCode}} | restarts {{.RestartCount}}' $(docker ps -aq)
```

```text
/api | alpine:3.23 | running | exit 0 | restarts 0
/web | nginx:1.30-alpine | running | exit 0 | restarts 0
```

`docker inspect` accepts several containers and applies the template to each. `docker ps --format` can show some of
these fields too, but only `inspect` has all of them (exit code, OOM, restart count, environment).
