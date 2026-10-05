# Lesson 071 · Logs

> Level 11 · Docker Compose · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

Docker collects everything a container's main process writes to **standard output and standard error**. `docker compose
logs` shows that output for every service of the project, interleaved and prefixed with the container name, or for one
service. The rule that makes it work: containers log to stdout/stderr, not to files inside the container.

## Visual

```text
 container api ─── stdout/stderr ──┐
 container redis ─ stdout/stderr ──┼──▶ Docker logging driver (json-file by default) ──▶ docker compose logs
 container worker  stdout/stderr ──┘                                                     [--tail N] [-t] [--since 5m]
                                                                                          [-f] [SERVICE ...]
 container worker ─▶ /var/log/worker.log   (a file inside the container: Docker never sees it)
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-071 examples/python-api
cp -r 10-compose/071-compose-logs/examples/. ~/docker-practice/lesson-071/
cd ~/docker-practice/lesson-071
docker compose up -d --build --quiet-build 2> /dev/null
```

The API (Gunicorn writes one access-log line per request), Redis, and a `worker` that logs a line every 2 seconds.

## Demonstration

Make a few requests, then read the API's last lines:

<!-- test: retry=15; contains=GET /visits; output -->
```bash
curl -s localhost:8080/visits > /dev/null; curl -s localhost:8080/health > /dev/null
docker compose logs --tail 2 api
```

```text
api-1  | 172.18.0.1 - - [05/Oct/2026:17:14:37 +0000] "GET /visits HTTP/1.1" 200 13 "-" "curl/8.19.0"
api-1  | 172.18.0.1 - - [05/Oct/2026:17:14:37 +0000] "GET /health HTTP/1.1" 200 16 "-" "curl/8.19.0"
```

All services together, with Docker's timestamps, only the last 2 lines of each:

<!-- test: contains=worker-1; output -->
```bash
docker compose logs -t --tail 2
```

```text
worker-1  | 2026-10-05T17:14:36.799139688Z worker: job 1 done
api-1     | 2026-10-05T17:14:37.262719091Z 172.18.0.1 - - [05/Oct/2026:17:14:37 +0000] "GET /visits HTTP/1.1" 200 13 "-" "curl/8.19.0"
api-1     | 2026-10-05T17:14:37.337771301Z 172.18.0.1 - - [05/Oct/2026:17:14:37 +0000] "GET /health HTTP/1.1" 200 16 "-" "curl/8.19.0"
redis-1   | 2026-10-05T17:14:36.796305679Z 1:M 05 Oct 2026 17:14:36.796 * Ready to accept connections tcp
redis-1   | 2026-10-05T17:14:36.796308620Z 1:M 05 Oct 2026 17:14:36.796 # WARNING: Redis does not require authentication and is not protected by network restrictions. Redis will accept connections from any IP address on any network interface.
```

Only what happened recently, without the prefix (useful for piping into `grep`):

<!-- test: contains=worker: job; output=tail:2 -->
```bash
docker compose logs --since 10s --no-log-prefix worker
```

```text
worker: job 1 done
```

To follow the logs live, add `-f` and stop with `Ctrl+C` (it never ends by itself):

<!-- test: skip -->
```bash
docker compose logs -f api worker
```

## Command breakdown

| Command / flag | What it does |
|---|---|
| `docker compose logs` | output of all services, interleaved |
| `docker compose logs SERVICE …` | only these services |
| `--tail N` | the last N lines per container |
| `-t`, `--timestamps` | prefix each line with the time Docker received it |
| `--since 10m`, `--until …` | a time window (`10s`, `5m`, `2h` or a date) |
| `-f`, `--follow` | keep streaming new lines |
| `--no-log-prefix` | without the `service-1 |` prefix |

## Hands-on lab

**Instructions.** Find every request to `/visits` in the API's logs, and count them.

**Expected result.** A number (1 or more, depending on how often you called it).

**Verification.**

<!-- test: contains=1 -->
```bash
cd ~/docker-practice/lesson-071
docker compose logs --no-log-prefix api | grep -c "GET /visits"
```

## Break it

The same worker, but written the "traditional" way: it appends to a log file.

<!-- test: absent=job; output -->
```bash
docker compose -p lesson-071-file -f broken/compose.yaml up -d 2> /dev/null
sleep 5
docker compose -p lesson-071-file -f broken/compose.yaml logs worker
echo "lines: $(docker compose -p lesson-071-file -f broken/compose.yaml logs worker | wc -l)"
```

```text
lines: 0
```

## Troubleshoot it

The container is running, but its log is empty. Docker only sees stdout and stderr; the process writes somewhere else.
Look inside the container:

<!-- test: contains=worker.log; contains=job; output -->
```bash
docker compose -p lesson-071-file -f broken/compose.yaml exec worker ls -l /var/log/worker.log
docker compose -p lesson-071-file -f broken/compose.yaml exec worker tail -2 /var/log/worker.log
```

```text
-rw-r--r--    1 root     root            76 Oct  5 17:14 /var/log/worker.log
worker: job 3 done
worker: job 4 done
```

The log exists only inside the container: `docker logs`, log collectors and dashboards cannot see it, it grows until the
disk is full, and it disappears with the container.

## Fix it

Write to stdout. When an application can only write to a file, point that file at stdout (the official Nginx image does
exactly this: `/var/log/nginx/access.log` is a link to `/dev/stdout`):

<!-- test: contains=worker: job; output=tail:2 -->
```bash
docker compose -p lesson-071-file -f broken/compose.yaml down 2> /dev/null
sed -i.bak 's# >> /var/log/worker.log##' broken/compose.yaml && rm broken/compose.yaml.bak
docker compose -p lesson-071-file -f broken/compose.yaml up -d 2> /dev/null
sleep 5
docker compose -p lesson-071-file -f broken/compose.yaml logs --no-log-prefix worker
```

```text
...
worker: job 2 done
worker: job 3 done
```

## Practice challenge

Show only the lines of the `worker` service that mention an even job number, with timestamps, from the main project.

<details>
<summary>Solution</summary>

<!-- test: contains=worker: job; output=tail:2 -->
```bash
cd ~/docker-practice/lesson-071
docker compose logs -t --no-log-prefix worker | grep -E "job [0-9]*[02468] done"
```

```text
...
2026-10-05T17:14:50.809757312Z worker: job 8 done
2026-10-05T17:14:54.812446960Z worker: job 10 done
```

`--no-log-prefix` keeps the lines clean for `grep`; `-t` adds Docker's timestamp, even when the application prints none.

</details>

## Real-world example

On a server, a team runs a log collector (Fluent Bit, Vector, the Datadog or CloudWatch agent) that reads every
container's stdout through Docker and ships it to central storage with the container's name and labels. It only works
because every service logs to stdout; a service writing to `/var/log/app.log` inside its container is invisible there,
which is usually discovered during an incident. Lesson 102 covers logging drivers.

## Recap

- Docker captures a container's stdout and stderr; `docker compose logs` shows them per project or per service.
- `--tail`, `-t`, `--since`, `-f`, `--no-log-prefix` narrow and shape the output.
- Log files inside the container are invisible to Docker: log to stdout (or link the file to `/dev/stdout`).

## Cleanup

<!-- test -->
```bash
cd ~/docker-practice/lesson-071
docker compose -p lesson-071-file -f broken/compose.yaml down -v 2> /dev/null
docker compose down -v --rmi local 2> /dev/null
rm -rf ~/docker-practice/lesson-071
```

The lab folder is gone: go back to the course folder (`cd` to where you cloned the course) before the next lesson.

Next: [Lesson 072 · exec and run](../072-compose-exec/README.md)
