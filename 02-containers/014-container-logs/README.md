# Lesson 014 · Container logs

> Level 3 · Working with containers · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

Docker captures everything a container's main process writes to **standard output** (stdout) and **standard error**
(stderr) and keeps it as the container's log. `docker logs` reads it, even after the container has stopped. This only
works if the application writes its logs to stdout/stderr: logs written to a file inside the container are invisible to
Docker. That is why official images such as Nginx redirect their log files to stdout.

## Visual

```text
  container "orders"                       Docker engine                       you
  ┌───────────────────────────┐           ┌──────────────────────────────┐
  │ app ── stdout ───────────▶│──────────▶│ log driver (json-file)       │──▶ docker logs orders
  │     ── stderr ───────────▶│──────────▶│ stores every line + time     │    docker logs -f  (follow)
  │     ── /var/log/app.log ✗ │  (never   │ kept until the container is  │    docker logs --tail 20
  └───────────────────────────┘  seen)    │ removed                      │    docker logs -t  (timestamps)
                                          └──────────────────────────────┘
```

## Lab setup

No files are needed.

## Demonstration

A container that writes some lines to stdout and an error to stderr, then exits:

<!-- test: contains=done -->
```bash
docker run -d --name orders alpine:3.23 sh -c '
  for i in 1 2 3 4 5; do echo "order $i accepted"; done
  echo "payment service unreachable" >&2
  exit 1' > /dev/null
sleep 1
echo done
```

The container has already exited, but its log is still there:

<!-- test: contains=payment service unreachable; output -->
```bash
docker logs orders
```

```text
payment service unreachable
order 1 accepted
order 2 accepted
order 3 accepted
order 4 accepted
order 5 accepted
```

The error may appear before the last order line although the program wrote it last: stdout and stderr are two
separate streams, and Docker does not guarantee the order of lines **between** them. Within one stream the order is
always kept. Only the last lines, with timestamps:

<!-- test: contains=order 5 accepted; output -->
```bash
docker logs --tail 2 -t orders
```

```text
2026-10-05T10:49:03.700617862Z order 4 accepted
2026-10-05T10:49:03.700619017Z order 5 accepted
```

`docker logs` sends the container's stdout to your stdout and its stderr to your stderr, so you can separate them:

<!-- test: contains=payment; absent=order; output -->
```bash
docker logs orders 2>&1 > /dev/null
```

```text
payment service unreachable
```

(`2>&1 > /dev/null` keeps only stderr: the errors.) For a running server, `-f` follows the log live, like `tail -f`;
stop with Ctrl+C:

<!-- test: skip -->
```bash
docker logs -f web
```

Nginx writes one line per request. Start it, send two requests (`--retry` waits until Nginx is ready), read the
access log:

<!-- test: contains=GET /missing; output=tail:2 -->
```bash
docker run -d --name web -p 8080:80 nginx:1.30-alpine > /dev/null
curl -s --retry 10 --retry-all-errors --retry-delay 1 http://localhost:8080/ > /dev/null
curl -s http://localhost:8080/missing > /dev/null
docker logs web 2>/dev/null | tail -2
```

```text
172.17.0.1 - - [05/Oct/2026:10:49:06 +0000] "GET / HTTP/1.1" 200 896 "-" "curl/8.19.0" "-"
172.17.0.1 - - [05/Oct/2026:10:49:06 +0000] "GET /missing HTTP/1.1" 404 153 "-" "curl/8.19.0" "-"
```

## Command breakdown

| Command / option | Meaning |
|---|---|
| `docker logs NAME` | the whole log (stdout and stderr) |
| `-f`, `--follow` | keep printing new lines (Ctrl+C to stop) |
| `--tail N` | only the last N lines |
| `-t`, `--timestamps` | prefix every line with its time |
| `--since 10m` / `--until …` | only a time range (`10m`, `1h`, or a date) |
| `2>&1 > /dev/null` | keep only the container's stderr |

## Hands-on lab

**Instructions.** Using `docker logs` with `--tail` and `grep`, show how many requests to `/missing` Nginx answered
with status `404`.

**Expected result.** `1` (one request to `/missing`, from the Demonstration).

**Verification.**

<!-- test: contains=1 -->
```bash
docker logs web 2>/dev/null | grep '"GET /missing' | grep -c ' 404 '
```

## Break it

An application writes its log to a file instead of stdout:

<!-- test: contains=log lines: 0; output -->
```bash
docker run -d --name filelogger alpine:3.23 sh -c 'while true; do echo "$(date) heartbeat" >> /var/log/app.log; sleep 1; done' > /dev/null
sleep 2
echo "log lines: $(docker logs filelogger 2>&1 | wc -l | tr -d ' ')"
```

```text
log lines: 0
```

## Troubleshoot it

The container is running, but `docker logs` is empty. Docker only sees stdout and stderr of the main process. Look
inside the container (`docker exec` runs a command in a running container, lesson 015):

<!-- test: contains=heartbeat; output -->
```bash
docker exec filelogger tail -2 /var/log/app.log
```

```text
Mon Oct  5 10:49:07 UTC 2026 heartbeat
Mon Oct  5 10:49:08 UTC 2026 heartbeat
```

The log exists, in a file Docker does not read. It also grows inside the container's writable layer until the disk is
full, and disappears when the container is removed.

## Fix it

Write to stdout. When you cannot change the application, do what the Nginx image does: make the log file a link to
the container's stdout:

<!-- test: contains=/dev/stdout; output -->
```bash
docker run --rm nginx:1.30-alpine ls -l /var/log/nginx/
```

```text
total 0
lrwxrwxrwx    1 root     root            11 Sep 22 21:19 access.log -> /dev/stdout
lrwxrwxrwx    1 root     root            11 Sep 22 21:19 error.log -> /dev/stderr
```

For our application, the fix is to print instead of appending to a file:

<!-- test: contains=heartbeat; retry=5 -->
```bash
docker rm -f filelogger > /dev/null
docker run -d --name filelogger alpine:3.23 sh -c 'while true; do echo "$(date) heartbeat"; sleep 1; done' > /dev/null 2>&1 || true
sleep 2
docker logs --tail 1 filelogger
```

## Practice challenge

A container crashes on start. Without running anything inside it, find out why from its log, and show the exit code.

<!-- test -->
```bash
docker run -d --name crasher alpine:3.23 sh -c 'echo "loading config /etc/app/config.yml"; cat /etc/app/config.yml'
```

<details>
<summary>Solution</summary>

<!-- test: contains=No such file; contains=exit code 1; output -->
```bash
sleep 1
docker logs crasher
docker inspect --format 'exit code {{.State.ExitCode}}' crasher
```

```text
loading config /etc/app/config.yml
cat: can't open '/etc/app/config.yml': No such file or directory
exit code 1
```

The log shows the last thing the program did and its error: the configuration file is missing. Logs survive the crash
because the container still exists; with `--rm` they would be gone with it (troubleshooting problem 01).

</details>

## Real-world example

In production, nobody runs `docker logs` on each server: a log driver or an agent (Fluent Bit, the CloudWatch driver,
Loki's Promtail) collects every container's stdout and ships it to central search (lesson 102). That only works if
every application logs to stdout, one event per line, which is one of the twelve-factor app rules that container
platforms, including Kubernetes (`kubectl logs`), rely on.

## Recap

- `docker logs` shows what the main process wrote to stdout and stderr, even after it exited.
- `--tail`, `-t`, `--since` and `-f` narrow and follow the log.
- Logs written to files inside the container are invisible to Docker: log to stdout, or link the file to `/dev/stdout`.
- Logs are deleted with the container.

## Cleanup

<!-- test -->
```bash
docker rm -f orders web filelogger crasher > /dev/null
```

Next: [Lesson 015 · Running commands in containers (exec)](../015-exec-into-containers/README.md)
