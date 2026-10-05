# Lesson 092 · HEALTHCHECK

> Level 15 · Observability · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

Docker knows whether a container's **process** is running. It does not know whether the application **works**. A
**health check** is a command that Docker runs inside the container at regular intervals: exit status 0 means healthy,
anything else counts as a failure. After `--retries` failures in a row, the container is marked **unhealthy**. Compose
(`depends_on: condition: service_healthy`, lesson 069), Swarm and monitoring tools act on that status.

## Visual

```text
  HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 CMD wget -q --spider http://127.0.0.1/ || exit 1

  docker run                 every interval, Docker runs the check INSIDE the container
      │
      ▼        first exit 0              exit 1 → exit 1 → exit 1  (3 in a row = retries)
  ┌──────────┐ ─────────────▶ ┌─────────┐ ─────────────────────────────────────▶ ┌───────────┐
  │ starting │                │ healthy │ ◀───────── any exit 0 ──────────────── │ unhealthy │
  └──────────┘                └─────────┘                                         └───────────┘
   failures during start-period do not count
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-092 14-observability/092-healthcheck/examples/broken 14-observability/092-healthcheck/examples/fixed
cd ~/docker-practice/lesson-092
cat fixed/Dockerfile
```

Two nginx images with a health check. The intervals are short (2 s) so that you do not wait in the lab; production
values are usually 10–30 s.

## Demonstration

A health check can also be given at start time, without changing the image. Start nginx with one:

<!-- test: contains=started web -->
```bash
docker run -d --name web --health-cmd 'wget -q --spider http://127.0.0.1/ || exit 1' \
  --health-interval 2s --health-retries 3 -p 8080:80 nginx:1.30-alpine > /dev/null && echo "started web"
```

Right after the start the status is `starting`; after the first successful check it is `healthy`. `docker ps` shows it
in the status column:

<!-- test: retry=20; contains=(healthy); output -->
```bash
docker ps --filter name=web --format '{{.Names}}: {{.Status}}'
```

```text
web: Up 2 seconds (healthy)
```

The details, including the output of the last checks, are in the container's state:

<!-- test: contains=ExitCode; output -->
```bash
docker inspect --format '{{.State.Health.Status}} {{.State.Health.FailingStreak}}' web
docker inspect --format '{{json (index .State.Health.Log 0)}}' web
```

```text
healthy 0
{"Start":"2026-10-05T16:57:47.881643806Z","End":"2026-10-05T16:57:47.932381825Z","ExitCode":0,"Output":""}
```

## Command breakdown

| Option (Dockerfile / `docker run`) | Meaning |
|---|---|
| `HEALTHCHECK CMD …` / `--health-cmd` | the check; exit 0 = healthy, 1 = unhealthy |
| `--interval` / `--health-interval` | time between checks (default 30 s) |
| `--timeout` / `--health-timeout` | a check running longer counts as failed (default 30 s) |
| `--start-period` / `--health-start-period` | failures during the start do not count (default 0 s) |
| `--retries` / `--health-retries` | failures in a row before `unhealthy` (default 3) |
| `HEALTHCHECK NONE` / `--no-healthcheck` | disable a check inherited from the base image |
| `.State.Health` | status, failing streak and the last 5 check results |

## Hands-on lab

**Instructions.** Build the image in `fixed/`, start it, and wait until it is healthy. Then list only healthy
containers with a filter.

**Expected result.** The container appears with `(healthy)` in its status.

**Verification.**

<!-- test: contains=started web-fixed -->
```bash
docker build -q -t cafe-web:health fixed > /dev/null
docker run -d --name web-fixed -p 8081:80 cafe-web:health > /dev/null && echo "started web-fixed"
```

<!-- test: retry=20; contains=web-fixed -->
```bash
docker ps --filter health=healthy --filter name=web-fixed --format '{{.Names}}: {{.Status}}'
```

## Break it

The `broken/` image checks the wrong port. Build and start it:

<!-- test: contains=started web-broken -->
```bash
docker build -q -t cafe-web:broken-health broken > /dev/null
docker run -d --name web-broken -p 8082:80 cafe-web:broken-health > /dev/null && echo "started web-broken"
```

<!-- test: retry=25; contains=(unhealthy); output -->
```bash
docker ps --filter name=web-broken --format '{{.Names}}: {{.Status}}'
```

```text
web-broken: Up 9 seconds (unhealthy)
```

## Troubleshoot it

The container is `Up`, and nginx actually serves pages:

<!-- test: contains=Welcome to nginx -->
```bash
curl -s http://localhost:8082/ | grep -o '<title>.*</title>'
```

So the **check** is wrong, not the application. Read what the check printed:

<!-- test: contains=Connection refused; output -->
```bash
docker inspect --format '{{range .State.Health.Log}}{{.ExitCode}} {{.Output}}{{end}}' web-broken | tail -2
docker inspect --format '{{json .Config.Healthcheck.Test}}' web-broken
```

```text
1 wget: can't connect to remote host (127.0.0.1): Connection refused

["CMD-SHELL","wget -q --spider http://127.0.0.1:8080/ || exit 1"]
```

`Connection refused` on `127.0.0.1:8080`: the check runs **inside** the container, where nginx listens on port 80.
`-p 8082:80` maps the host's port 8082 to the container's port 80; the container itself never sees 8082 or 8080.

## Fix it

The health check must use the container's own port (see `fixed/Dockerfile`). Replace the container with the fixed
image:

<!-- test: contains=started web-broken -->
```bash
docker rm -f web-broken > /dev/null
docker run -d --name web-broken -p 8082:80 cafe-web:health > /dev/null && echo "started web-broken"
```

<!-- test: retry=20; contains=(healthy) -->
```bash
docker ps --filter name=web-broken --format '{{.Names}}: {{.Status}}'
```

## Practice challenge

Make a healthy container unhealthy on purpose: in `web-fixed`, delete the page nginx serves
(`/usr/share/nginx/html/index.html`) and watch the status change. Explain why `wget --spider` now fails.

<details>
<summary>Solution</summary>

<!-- test: contains=done -->
```bash
docker exec web-fixed rm /usr/share/nginx/html/index.html && echo done
```

<!-- test: retry=25; contains=(unhealthy); output -->
```bash
docker ps --filter name=web-fixed --format '{{.Names}}: {{.Status}}'
docker inspect --format '{{range .State.Health.Log}}{{.Output}}{{end}}' web-fixed | grep . | tail -1
```

```text
web-fixed: Up 34 seconds (unhealthy)
wget: server returned error: HTTP/1.1 403 Forbidden
```

Without `index.html`, nginx answers `/` with an error status (403, directory listing is off), and `wget` exits with a
non-zero status for HTTP errors. Three failures in a row → `unhealthy`. A good health check tests what users need, not
just "is the port open".

</details>

## Real-world example

Base images such as databases ship health checks (`pg_isready` for PostgreSQL, `redis-cli ping` for Redis are common
choices in Compose files). In Compose, an API service waits with `depends_on: db: condition: service_healthy` until the
database answers, instead of crashing at start (lesson 069). Kubernetes ignores the Dockerfile `HEALTHCHECK` and uses
its own liveness and readiness probes, configured the same way (command or HTTP request, period, timeout, failure
threshold).

## Recap

- A health check is a command run inside the container; exit 0 = healthy.
- Status: `starting` → `healthy` or, after `retries` failures in a row, `unhealthy`.
- Check from inside the container: use the container's port, and a tool that exists in the image.
- Read failures in `docker inspect --format '{{json .State.Health}}'`.

## Cleanup

<!-- test -->
```bash
docker rm -f web web-fixed web-broken > /dev/null 2>&1 || true
docker image rm -f cafe-web:health cafe-web:broken-health > /dev/null
cd ~ && rm -rf ~/docker-practice/lesson-092
```

Next: [Lesson 093 · Running is not healthy](../093-running-is-not-healthy/README.md)
