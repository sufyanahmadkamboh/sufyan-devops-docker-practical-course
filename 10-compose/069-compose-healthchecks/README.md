# Lesson 069 · Healthchecks in Compose

> Level 11 · Docker Compose · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

A **healthcheck** is a command Docker runs inside the container at a regular interval. Exit code 0 means healthy, any
other code means a failed check; after a number of failures in a row, the container is **unhealthy**. Compose uses
health for `depends_on` conditions (lesson 068) and for `docker compose up --wait`; you see it in `docker compose ps`.
A process that is running but not answering is exactly what a healthcheck catches (lesson 093).

## Visual

```text
             start_period (failures do not count)
 created ──▶ starting ──────────────────────────▶ healthy ◀────────┐
                 │   check every `interval`           │   check ok │
                 │   (each may take up to `timeout`)  │            │
                 │                                    ▼ check fails│
                 └─── `retries` failures in a row ──▶ unhealthy ───┘ (a passing check makes it healthy again)

 test: ["CMD", "redis-cli", "ping"]          the command, run directly
 test: ["CMD-SHELL", "pg_isready || exit 1"] the command, run by /bin/sh
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-069 examples/python-api
cp -r 10-compose/069-compose-healthchecks/examples/. ~/docker-practice/lesson-069/
cd ~/docker-practice/lesson-069
cat compose.yaml
```

## Demonstration

`--wait` makes `up` return only when every service is healthy (or fails if one is not):

<!-- test: contains=healthy; output -->
```bash
docker compose up -d --build --quiet-build --wait 2> /dev/null
docker compose ps --format '{{.Service}}: {{.Status}}'
```

```text
api: Up 6 seconds (healthy)
redis: Up 8 seconds (healthy)
```

Redis started first; `api` was created only when Redis was healthy (its `depends_on` condition). The history of the
last checks is stored on the container:

<!-- test: contains=ExitCode=0; output -->
```bash
docker inspect lesson-069-api-1 --format '{{.State.Health.Status}}: {{range .State.Health.Log}}ExitCode={{.ExitCode}} {{end}}'
```

```text
healthy: ExitCode=0 
```

## Command breakdown

| Key / command | Meaning |
|---|---|
| `healthcheck: test:` | the check; `CMD` runs it directly, `CMD-SHELL` through `/bin/sh -c` |
| `interval`, `timeout`, `retries`, `start_period` | how often, how long each check may take, failures before unhealthy, grace at start |
| `docker compose up --wait` | return when all services are running and healthy; fail otherwise |
| `--wait-timeout N` | give up after N seconds |
| `{{.State.Health.Status}}`, `{{.State.Health.Log}}` | the health status and the last checks (with their output) |

## Hands-on lab

**Instructions.** Watch Redis's healthcheck work: run its check command yourself, then read the output of the last check
Docker recorded.

**Expected result.** `PONG` both times.

**Verification.**

<!-- test: contains=PONG -->
```bash
cd ~/docker-practice/lesson-069
docker compose exec redis redis-cli ping
docker inspect lesson-069-redis-1 --format '{{range .State.Health.Log}}{{.Output}}{{end}}' | tail -1
```

## Break it

A teammate changes the port the healthcheck uses (`5001` instead of the API's `5000`):

<!-- test: fail; anyof=unhealthy||is not healthy; output -->
```bash
cp compose.yaml compose.good.yaml
cp broken/compose.yaml compose.yaml
docker compose up -d --wait --wait-timeout 40 2>&1 | tail -1
test "${PIPESTATUS[0]}" -eq 0
```

```text
container lesson-069-api-1 is unhealthy
```

## Troubleshoot it

`unhealthy`, although the API itself works:

<!-- test: contains=ok; output -->
```bash
curl -s localhost:8080/health
```

```text
{"status":"ok"}
```

So the check is wrong, not the application. Read what the checks printed:

<!-- test: contains=Connection refused; output -->
```bash
docker inspect lesson-069-api-1 --format '{{range .State.Health.Log}}{{.ExitCode}} {{.Output}}{{end}}' | grep -o "ConnectionRefusedError.*" | tail -1
docker inspect lesson-069-api-1 --format '{{json .Config.Healthcheck.Test}}'
```

```text
ConnectionRefusedError: [Errno 111] Connection refused
["CMD","python","-c","import urllib.request; urllib.request.urlopen('http://127.0.0.1:5001/health', timeout=2)"]
```

The check connects to port 5001, where nothing listens. A healthcheck tests the container from **inside**: it must use
the container port the application listens on.

## Fix it

<!-- test: contains=healthy -->
```bash
cp compose.good.yaml compose.yaml
docker compose up -d --wait 2> /dev/null
docker compose ps --format '{{.Service}}: {{.Status}}'
```

## Practice challenge

Redis's check is `redis-cli ping | grep -q PONG`: it passes only when Redis really answers. Make Redis unusable for
clients without stopping it, by requiring a password (`redis-cli CONFIG SET requirepass x`). Show that the container
turns `unhealthy`, then undo the change and show it turns `healthy` again.

<details>
<summary>Solution</summary>

<!-- test: contains=unhealthy; contains=healthy again; output -->
```bash
cd ~/docker-practice/lesson-069
docker compose exec redis redis-cli CONFIG SET requirepass x > /dev/null
docker compose exec redis redis-cli ping
sleep 25
echo "after 25 s: $(docker inspect lesson-069-redis-1 --format '{{.State.Health.Status}}')"
docker compose exec redis redis-cli -a x --no-auth-warning CONFIG SET requirepass "" > /dev/null
sleep 3
echo "after the undo: $(docker inspect lesson-069-redis-1 --format '{{.State.Health.Status}}') again"
```

```text
NOAUTH Authentication required.

after 25 s: unhealthy
after the undo: healthy again
```

Without a password, `PING` gets `NOAUTH` instead of `PONG`, so `grep -q PONG` fails and, after 10 failed checks 2 s
apart, the container is `unhealthy`. Whether the plain `redis-cli ping` would have noticed depends on its exit code for
an error reply; matching the expected answer does not depend on such details. A good check fails whenever the service
is unusable.

</details>

## Real-world example

A team's API kept running after it lost its database connection pool: the process was alive, every request failed, and
nothing restarted it. They added a `/health` endpoint that checks the pool, a healthcheck that calls it, and an alert on
`unhealthy`. On Kubernetes, the same endpoint feeds the liveness and readiness probes.

## Recap

- A healthcheck is a command run inside the container; exit 0 = check passed.
- `retries` failures in a row → `unhealthy`; `start_period` gives the service time to start.
- `docker compose up --wait` and `condition: service_healthy` use health.
- Check the check: it runs inside the container, on container ports, and must fail when the service is unusable.

## Cleanup

<!-- test -->
```bash
cd ~/docker-practice/lesson-069
docker compose down -v --rmi local 2> /dev/null
rm -rf ~/docker-practice/lesson-069
```

The lab folder is gone: go back to the course folder (`cd` to where you cloned the course) before the next lesson.

Next: [Lesson 070 · Profiles](../070-compose-profiles/README.md)
