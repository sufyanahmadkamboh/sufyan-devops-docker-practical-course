# Troubleshooting problem 21 · Healthcheck failure

> ⏱ 15 minutes · run every command from the course folder · related lessons: 069, 092, 093

## Problem

The menu API answers every request, but Docker reports it as `unhealthy`. In Compose, the services that wait for it
(`depends_on: condition: service_healthy`) never start.

## Symptoms

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh trouble-21 17-troubleshooting/21-healthcheck-failure/examples
cd ~/docker-practice/trouble-21
docker build -q -t menu-api:broken broken > /dev/null
docker run -d --name menu-api -p 8080:8080 menu-api:broken > /dev/null
```

<!-- test: retry=15; contains=(unhealthy); output -->
```bash
docker ps --filter name=menu-api --format '{{.Names}}: {{.Status}}'
```

```text
menu-api: Up 4 seconds (unhealthy)
```

Yet the application works:

<!-- test: retry=5; contains=ok; output -->
```bash
curl -s http://localhost:8080/health
```

```text
ok
```

## Investigation

**1. What does the healthcheck run?**

<!-- test: contains=curl; output -->
```bash
docker image inspect --format '{{json .Config.Healthcheck.Test}}' menu-api:broken
```

```text
["CMD-SHELL","curl -fs http://localhost:8080/health || exit 1"]
```

**2. What did the last checks return?** Docker keeps the last five results, with their output:

<!-- test: contains=curl: not found; output -->
```bash
docker inspect --format '{{range .State.Health.Log}}exit {{.ExitCode}}: {{.Output}}{{end}}' menu-api | head -2
docker inspect --format 'failing streak: {{.State.Health.FailingStreak}}' menu-api
```

```text
exit 1: /bin/sh: 1: curl: not found
exit 1: /bin/sh: 1: curl: not found
failing streak: 2
```

**3. Run the check command yourself, inside the container:**

<!-- test: contains=not found; output -->
```bash
docker exec menu-api sh -c 'curl -fs http://localhost:8080/health || echo "exit $?"' 2>&1
```

```text
exit 127
sh: 1: curl: not found
```

## Commands

| Command | What it tells you |
|---|---|
| `docker ps` | `(healthy)`, `(unhealthy)` or `(health: starting)` after `Up …` |
| `docker inspect --format '{{json .Config.Healthcheck}}' NAME` | the check command, interval, timeout, retries |
| `docker inspect --format '{{range .State.Health.Log}}…{{end}}' NAME` | exit code and output of the last checks |
| `docker exec NAME sh -c 'CHECK'` | the check run by hand, with its full error |

## Output interpretation

The check fails with exit code 1 and `curl: not found`: the healthcheck is broken, not the application.
`python:3.14-slim` contains no `curl`, so the `|| exit 1` turns "command not found" into "unhealthy". Read the
health log before debugging the application: a check that times out, uses the wrong port or host, or a tool missing
from the image all look like an unhealthy service (lesson 093).

## Root cause

The `HEALTHCHECK` uses `curl`, which is not installed in the image.

## Fix

Check with a tool the image really contains (here Python itself), rather than installing `curl` only for the check:

<!-- test: contains=urllib; output -->
```bash
grep -n HEALTHCHECK -A1 fixed/Dockerfile
```

```text
6:HEALTHCHECK --interval=2s --timeout=2s --retries=2 \
7-  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=2)"]
```

<!-- test -->
```bash
docker rm -f menu-api > /dev/null
docker build -q -t menu-api:fixed fixed > /dev/null
docker run -d --name menu-api -p 8080:8080 menu-api:fixed > /dev/null
```

## Verification

<!-- test: retry=15; contains=(healthy); output -->
```bash
docker ps --filter name=menu-api --format '{{.Names}}: {{.Status}}'
```

```text
menu-api: Up 2 seconds (healthy)
```

<!-- test: contains=exit 0; output -->
```bash
docker inspect --format '{{range .State.Health.Log}}exit {{.ExitCode}}{{println}}{{end}}' menu-api | grep exit | tail -n 1
```

```text
exit 0
```

## Prevention

- Test the healthcheck command in the image when you write it: `docker run --rm IMAGE sh -c 'CHECK'`.
- Use what the image has: `wget` in Alpine/BusyBox, the language runtime in slim images, a small `healthcheck`
  binary in distroless images (lesson 092).
- Check the address the app really listens on (`127.0.0.1:PORT` from inside works only if it binds there or to
  `0.0.0.0`), and keep the timeout shorter than the interval.

## Cleanup

<!-- test -->
```bash
docker rm -f menu-api > /dev/null
docker image rm menu-api:broken menu-api:fixed > /dev/null
rm -rf ~/docker-practice/trouble-21
```

Next: [Problem 22 · Memory limit exceeded](../22-memory-limit-exceeded/README.md)
