<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 004 · Docker architecture · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Point the client at an address where no daemon is listening (`DOCKER_HOST` overrides the context):

```bash
DOCKER_HOST=tcp://127.0.0.1:1 docker version --format '{{.Server.Version}}' 2>&1
```

```text

error during connect: Get "http://127.0.0.1:1/v1.54/version": dial tcp 127.0.0.1:1: connectex: No connection could be made because the target machine actively refused it.
```

## Troubleshoot it

The client works (it printed an error, it did not crash) but it cannot reach any daemon. The message names the address
it tried: `127.0.0.1:1`. On Linux the same mistake reads `Cannot connect to the Docker daemon at …` or
`connection refused`. Every "cannot connect" error has one of three causes:

1. the daemon is not running (Docker Desktop stopped, `systemctl status docker` on Linux),
2. the client points to the wrong place (`DOCKER_HOST`, or the wrong context),
3. you may not use the socket (on Linux: not in the `docker` group, so `permission denied`).

Check where the client is pointing:

```bash
echo "DOCKER_HOST=${DOCKER_HOST:-(not set)}"
echo "context: $(docker context show)"
```

## Fix it

Remove the override (in a real shell: `unset DOCKER_HOST`, and remove it from your shell profile if it is set there), so
the client uses its active context again:

```bash
unset DOCKER_HOST
docker version --format '{{.Server.Version}}' > /dev/null && echo "server is reachable"
```
