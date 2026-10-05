<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 089 · Multi-stage builds for Go · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Without a shell in the image, how do you debug the running `go-distroless` container's network? Start a throw-away
`busybox:1.37` container that **shares its network namespace** (`--network container:NAME`) and call the API's
`/health` endpoint on `localhost` from there.

## Solution

```bash
docker run --rm --network container:go-distroless busybox:1.37 wget -qO- http://localhost:8080/health
```

```text
{"status":"ok"}
```

The debug container sees the same network interfaces and `localhost` as the distroless one, with all of BusyBox's
tools. Docker Desktop also offers `docker debug`, which attaches a toolbox to a running container in a similar way.
Lesson 052 uses this technique for network troubleshooting.
