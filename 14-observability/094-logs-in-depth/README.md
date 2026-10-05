# Lesson 094 · Logs in depth

> Level 15 · Observability · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

Docker captures everything a container's main process writes to **standard output** (stdout) and **standard error**
(stderr), and stores it through a **logging driver** (by default `json-file`, lesson 102). `docker logs` reads it back.
Lesson 014 covered the basics; this lesson covers the parts that matter when something is wrong: the two streams,
time filters, timestamps, and the most common reason logs are missing: **output buffering**.

## Visual

```text
  container                                    Docker                              you
  ┌──────────────────────────┐   stdout  ──▶  ┌──────────────────────────┐        docker logs NAME
  │ main process (PID 1)     │   stderr  ──▶  │ logging driver (json-file)│ ──▶    --tail N   --since 1m
  │  print("INFO …")         │                │ one file per container,  │        -t (timestamps)  -f (follow)
  │  print("ERROR …", stderr)│                │ kept until docker rm     │        2>/dev/null (stdout only)
  └──────────────────────────┘                └──────────────────────────┘
       ✗ writes to /var/log/app.log  → never reaches Docker
       ✗ buffers stdout (Python, C) → appears late, or only at exit
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-094 14-observability/094-logs-in-depth/examples
cd ~/docker-practice/lesson-094
cat worker.py
```

## Demonstration

nginx writes its access log to stdout and its error/notice log to stderr. Start it and make two requests:

<!-- test: contains=started web -->
```bash
docker run -d --name web -p 8080:80 nginx:1.30-alpine > /dev/null && echo "started web"
```

<!-- test: retry=10; contains=200 -->
```bash
curl -s -w '\n%{http_code}\n' http://localhost:8080/ | tail -n 1
curl -s -w '\n%{http_code}\n' http://localhost:8080/missing | tail -n 1
```

The last two lines, with Docker's timestamps:

<!-- test: contains=GET /missing; output -->
```bash
docker logs -t --tail 2 web
```

```text
2026-10-05T16:59:33.702957630Z 172.17.0.1 - - [05/Oct/2026:16:59:33 +0000] "GET /missing HTTP/1.1" 404 153 "-" "curl/8.19.0" "-"
2026-10-05T16:59:33.702957275Z 2026/10/05 16:59:33 [error] 31#31: *2 open() "/usr/share/nginx/html/missing" failed (2: No such file or directory), client: 172.17.0.1, server: localhost, request: "GET /missing HTTP/1.1", host: "localhost:8080"
```

`docker logs` keeps the two streams apart: the container's stdout goes to your stdout, its stderr to your stderr.
Show only one of them by discarding the other:

<!-- test: contains=stdout lines; contains=stderr lines; output -->
```bash
echo "stdout lines: $(docker logs web 2>/dev/null | wc -l)"
echo "stderr lines: $(docker logs web 2>&1 >/dev/null | wc -l)"
```

```text
stdout lines: 11
stderr lines: 21
```

Only recent lines, by time:

<!-- test: contains=GET /missing -->
```bash
docker logs --since 1m web 2>/dev/null
```

## Command breakdown

| Command | What it does |
|---|---|
| `docker logs NAME` | everything the container wrote to stdout and stderr since it was created |
| `--tail N` | only the last N lines |
| `-t` | prefix each line with the time Docker received it |
| `--since 10m` / `--until 2026-10-05T10:00:00` | a time window (relative or absolute) |
| `-f` | follow: keep printing new lines until Ctrl+C or until the container stops |
| `docker logs NAME 2>/dev/null` | the container's stdout only |
| `docker logs NAME 2>&1 >/dev/null` | the container's stderr only |

## Hands-on lab

**Instructions.** `docker logs -f` follows a log until you press Ctrl+C, or until the container stops. Start a short
job that prints a line every second for three seconds, and follow its log from the start.

**Expected result.** The three lines appear one per second, and the command returns by itself when the job ends.

**Verification.**

<!-- test: contains=tick 3 -->
```bash
docker run -d --name ticker alpine:3.23 sh -c 'for i in 1 2 3; do echo "tick $i"; sleep 1; done' > /dev/null
docker logs -f -t ticker
```

## Break it

Start the worker, which processes an order every half second, and look at its logs after a few seconds:

<!-- test: contains=started worker -->
```bash
docker run -d --name worker -v "$(pwd)/worker.py:/worker.py:ro" python:3.14-alpine python /worker.py > /dev/null && echo "started worker"
```

<!-- test: contains=ERROR; absent=INFO; output -->
```bash
sleep 4
docker logs worker
```

```text
ERROR order 5: payment declined
```

Only errors. Did the worker process anything at all?

## Troubleshoot it

The process is running:

<!-- test: contains=worker.py -->
```bash
docker top worker -o pid,args
```

And the code prints an `INFO` line for every successful order. The `INFO` lines are written to **stdout**, the
`ERROR` lines to **stderr**. When stdout is not a terminal (in a container, it is a pipe to Docker), Python collects
stdout in an 8 KB buffer and writes it out only when the buffer is full or the program exits; stderr is written line
by line. The lines exist, they are just stuck in the buffer. Proof: with a terminal (`-t`), Python does not buffer:

<!-- test: contains=INFO order 1: processed -->
```bash
docker run -d --name worker-tty -t -v "$(pwd)/worker.py:/worker.py:ro" python:3.14-alpine python /worker.py > /dev/null
sleep 2
docker logs worker-tty | head -2
docker rm -f worker-tty > /dev/null
```

`-t` is a workaround for a test, not a fix: it mixes stdout and stderr into one stream.

## Fix it

Tell Python not to buffer: `PYTHONUNBUFFERED=1` (in a Dockerfile: `ENV PYTHONUNBUFFERED=1`; or `python -u`):

<!-- test: contains=started worker -->
```bash
docker rm -f worker > /dev/null
docker run -d --name worker -e PYTHONUNBUFFERED=1 -v "$(pwd)/worker.py:/worker.py:ro" python:3.14-alpine python /worker.py > /dev/null && echo "started worker"
```

<!-- test: contains=INFO order 1: processed; contains=ERROR order 5; output -->
```bash
sleep 3
docker logs worker | head -5
```

```text
ERROR order 5: payment declined
INFO order 1: processed
INFO order 2: processed
INFO order 3: processed
INFO order 4: processed
INFO order 6: processed
```

Every line arrives as it is written, in order.

## Practice challenge

Using only `docker logs` and shell redirection, count how many orders the worker has reported as **failed** so far,
and print the last failure with its Docker timestamp.

<details>
<summary>Solution</summary>

<!-- test: contains=failed orders:; contains=ERROR order; output -->
```bash
echo "failed orders: $(docker logs worker 2>&1 >/dev/null | wc -l)"
docker logs -t worker 2>&1 >/dev/null | tail -1
```

```text
failed orders: 1
2026-10-05T16:59:49.006353363Z ERROR order 5: payment declined
```

`2>&1 >/dev/null` sends the container's stderr into the pipe and discards its stdout (the order of the redirections
matters). Because the worker writes errors to stderr, no `grep` is needed.

</details>

## Real-world example

Logging platforms (Loki, Elasticsearch, CloudWatch, Datadog) collect container logs from the logging driver or from the
log files on each host, not from files inside containers. A team that moves a service into containers therefore makes
it log to stdout/stderr, one event per line (often JSON), with `PYTHONUNBUFFERED=1` or the equivalent for its runtime.
Official images such as nginx link their log files to `/dev/stdout` and `/dev/stderr` for exactly this reason.

## Recap

- Docker captures the main process's stdout and stderr; `docker logs` keeps them as separate streams.
- `--tail`, `--since`, `--until`, `-t` and `-f` narrow down what you read.
- Missing log lines with a running process: suspect output buffering (`PYTHONUNBUFFERED=1`) or logs written to a file.
- Write errors to stderr and everything else to stdout, one event per line.

## Cleanup

<!-- test -->
```bash
docker rm -f web worker worker-tty ticker > /dev/null 2>&1 || true
cd ~ && rm -rf ~/docker-practice/lesson-094
```

Next: [Lesson 095 · docker stats](../095-docker-stats/README.md)
