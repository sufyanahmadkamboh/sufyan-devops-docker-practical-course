# Lesson 093 · Running is not healthy

> Level 15 · Observability · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

`docker ps` says `Up`, the process exists, and yet nobody gets an answer: the application is stuck (a deadlock, a
request waiting forever, an exhausted connection pool). Docker restarts containers only when their process **exits**;
a hung process never exits. This lesson shows the difference between **running** and **healthy**, how to detect a hung
application, and why Docker on its own does not repair it.

## Visual

```text
                       process alive?      answers requests?     docker ps                   docker restart policy
  working app          yes                 yes                   Up 2 minutes (healthy)      nothing to do
  crashed app          no (exited)         no                    Exited (1)                  restarts it  ✓
  hung app             yes                 NO                    Up 2 minutes (unhealthy)    does nothing ✗

  Only a health check sees the third case. Acting on it is the job of an orchestrator (Swarm, Kubernetes),
  a monitoring system, or you.
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-093 14-observability/093-running-is-not-healthy/examples/single 14-observability/093-running-is-not-healthy/examples/threaded
cd ~/docker-practice/lesson-093
grep -n "sleep\|HTTPServer(" single/app.py
```

A small API with a realistic bug: `GET /report` waits forever (as if for a slow dependency without a timeout). The
image has a health check: `/health` must answer within 2 seconds.

## Demonstration

Build the `single` version, start it with a restart policy, and wait until it is healthy:

<!-- test: contains=started api -->
```bash
docker build -q -t cafe-api:single single > /dev/null
docker run -d --name api --restart always -p 8080:8080 cafe-api:single > /dev/null && echo "started api"
```

<!-- test: retry=20; contains=(healthy); output -->
```bash
curl -s http://localhost:8080/health
docker ps --filter name=api --format '{{.Names}}: {{.Status}}'
```

```text
ok
api: Up 7 seconds (healthy)
```

## Command breakdown

| Command | What it shows |
|---|---|
| `docker inspect --format '{{.State.Status}}'` | the process state: `running`, `exited`, `restarting`, … |
| `docker inspect --format '{{.State.Health.Status}}'` | the health state: `starting`, `healthy`, `unhealthy` |
| `docker inspect --format '{{.RestartCount}}'` | how often the restart policy restarted the container |
| `curl -m 2 URL` | give up after 2 seconds instead of waiting forever |
| `docker ps --filter health=unhealthy` | every unhealthy container on the host |

## Hands-on lab

**Instructions.** Show both states of the `api` container side by side with one `docker inspect --format` command.

**Expected result.** `state=running health=healthy restarts=0`.

**Verification.**

<!-- test: contains=state=running health=healthy restarts=0 -->
```bash
docker inspect --format 'state={{.State.Status}} health={{.State.Health.Status}} restarts={{.RestartCount}}' api
```

## Break it

One user requests the report:

<!-- test: contains=gave up; output -->
```bash
curl -s -m 2 http://localhost:8080/report || echo "gave up after 2 seconds"
```

```text
gave up after 2 seconds
```

## Troubleshoot it

Now nothing answers, not even `/health`:

<!-- test: contains=no answer; output -->
```bash
curl -s -m 2 http://localhost:8080/health || echo "no answer from /health"
```

```text
no answer from /health
```

What does Docker think?

<!-- test: retry=25; contains=state=running health=unhealthy restarts=0; output -->
```bash
docker inspect --format 'state={{.State.Status}} health={{.State.Health.Status}} restarts={{.RestartCount}}' api
```

```text
state=running health=unhealthy restarts=0
```

The process is `running` and the restart policy `always` did nothing (`restarts=0`): it reacts only to exits. The
health check is the one signal that something is wrong. Its log says what it saw:

<!-- test: anyof=timed out||Health check exceeded timeout; output -->
```bash
docker inspect --format '{{range .State.Health.Log}}{{.Output}}{{end}}' api | grep . | tail -1
```

```text
TimeoutError: timed out
```

The root cause is in the code: this server handles **one request at a time** (`HTTPServer`), so the stuck `/report`
request blocks every other request, including the health check.

## Fix it

Short term: restart the hung container (this is what an orchestrator would do automatically for an unhealthy one):

<!-- test: contains=restarted -->
```bash
docker restart api > /dev/null && echo "restarted"
```

<!-- test: retry=20; contains=health=healthy -->
```bash
docker inspect --format 'state={{.State.Status}} health={{.State.Health.Status}}' api
```

Real fix: change the code. The `threaded` version handles every request in its own thread, so one stuck request does
not block the others (the endpoint itself still needs a timeout on its dependency):

<!-- test: contains=started api -->
```bash
docker rm -f api > /dev/null
docker build -q -t cafe-api:threaded threaded > /dev/null
docker run -d --name api --restart always -p 8080:8080 cafe-api:threaded > /dev/null && echo "started api"
```

<!-- test: retry=20; contains=health=healthy -->
```bash
docker inspect --format 'health={{.State.Health.Status}}' api
```

<!-- test: contains=/health still ok; output -->
```bash
curl -s -m 2 http://localhost:8080/report || echo "/report gave up after 2 seconds"
curl -s -m 2 http://localhost:8080/health > /dev/null && echo "/health still ok"
```

```text
/report gave up after 2 seconds
/health still ok
```

## Practice challenge

Write a one-line "watchdog" that finds every unhealthy container on the host and restarts it. Test it by breaking the
`single` version again.

<details>
<summary>Solution</summary>

<!-- test: contains=started api-single -->
```bash
docker run -d --name api-single -p 8081:8080 cafe-api:single > /dev/null && echo "started api-single"
```

<!-- test: retry=20; contains=healthy -->
```bash
docker inspect --format '{{.State.Health.Status}}' api-single
```

<!-- test: contains=gave up -->
```bash
curl -s -m 2 http://localhost:8081/report || echo "gave up"
```

<!-- test: retry=25; contains=api-single -->
```bash
docker ps --filter health=unhealthy --format '{{.Names}}'
```

<!-- test: contains=api-single; output -->
```bash
docker ps --filter health=unhealthy --format '{{.Names}}' | xargs -r docker restart
```

```text
api-single
```

`docker ps --filter health=unhealthy` finds them (by name) and `xargs -r docker restart` restarts them (`-r`: do
nothing when the list is empty). Run regularly (cron, a systemd timer), this is a minimal version of what Kubernetes'
liveness probe does. In production, prefer the platform's own mechanism and alerting over a homemade script.

</details>

## Real-world example

A Java service runs out of database connections after a network blip: every request waits for a connection that
never comes. The JVM is up, the port is open, `docker ps` shows `Up`, and users get time-outs. A health check that
calls an endpoint which actually uses the database marks the container unhealthy within seconds; Kubernetes' liveness
probe restarts it, the alert reaches the on-call engineer, and the connection pool settings get fixed.

## Recap

- `running` describes the process; `healthy` describes the application. They can disagree.
- Restart policies act only when the process exits; a hung process is never restarted by them.
- Find hung containers with health checks: `docker ps --filter health=unhealthy`.
- Restarting fixes the symptom; timeouts and concurrency in the code fix the cause.

## Cleanup

<!-- test -->
```bash
docker rm -f api api-single > /dev/null 2>&1 || true
docker image rm -f cafe-api:single cafe-api:threaded > /dev/null
cd ~ && rm -rf ~/docker-practice/lesson-093
```

Next: [Lesson 094 · Logs in depth](../094-logs-in-depth/README.md)
