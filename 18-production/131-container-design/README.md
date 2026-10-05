# Lesson 131 · Container design

> Level 19 · Production · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

A container that works is not automatically a container that is easy to run. Production platforms (Docker hosts,
Kubernetes, ECS) expect every container to follow a few rules: **one concern per container**, **logs on standard
output**, **no important state inside the container**, **configuration from outside**, and a **clean shutdown on
SIGTERM**. A container that follows them can be restarted, replaced, scaled and debugged by anyone, with the standard
tools.

## Visual

```text
 Designed for production                                 Fights the platform

 ┌─────────── container ───────────┐                     ┌─────────── container ───────────┐
 │ one service (nginx, the API, …) │                     │ API + database + cron + sshd    │
 │ logs ──▶ stdout/stderr ─────────┼──▶ docker logs,     │ logs ──▶ /var/log/app.log       │──▶ invisible
 │ state ──▶ volume / database     │    log collectors   │ uploads ──▶ /app/uploads        │──▶ lost on rm
 │ config ◀── env, mounted files   │                     │ config baked in per environment │──▶ one image per env
 │ SIGTERM ──▶ finish, exit 0      │                     │ ignores SIGTERM ──▶ killed      │──▶ dropped requests
 └─────────────────────────────────┘                     └─────────────────────────────────┘
   disposable: rm + run = same service                     a pet: nobody dares to replace it
```

| Principle | Why | Lesson |
|---|---|---|
| One concern per container | scale, update and restart each part on its own | 013, 062 |
| Logs to stdout/stderr | `docker logs` and every log collector read exactly that | 014, 094 |
| State outside the container | the container can be deleted and recreated at any time | 055, 058 |
| Configuration from outside | the same image runs in every environment | 059, 133 |
| Handle SIGTERM | stopping or replacing a container drops no requests | 130 |

## Lab setup

No files are needed: this lesson uses the official `nginx` and `alpine` images.

## Demonstration

The official Nginx image is a good example of the rules. Nginx normally writes its logs to files; the image turns
those files into links to the container's standard output and error:

<!-- test: contains=/dev/stdout; output -->
```bash
docker run --rm nginx:1.30-alpine ls -l /var/log/nginx
```

```text
total 0
lrwxrwxrwx    1 root     root            11 Sep 22 21:19 access.log -> /dev/stdout
lrwxrwxrwx    1 root     root            11 Sep 22 21:19 error.log -> /dev/stderr
```

So every request ends up in `docker logs`, without any extra tool:

<!-- test: contains=nginx:1.30-alpine -->
```bash
docker run -d --name web -p 8080:80 nginx:1.30-alpine > /dev/null
docker ps --filter name=web --format '{{.Names}} {{.Image}} {{.Status}}'
```

<!-- test: retry=10; contains=200; output -->
```bash
curl -sI http://localhost:8080/ | head -1
docker logs web 2>/dev/null | grep '"HEAD / HTTP'
```

```text
HTTP/1.1 200 OK
172.17.0.1 - - [05/Oct/2026:12:16:37 +0000] "HEAD / HTTP/1.1" 200 0 "-" "curl/8.19.0" "-"
```

One concern: the container runs Nginx and nothing else (a master process and its workers):

<!-- test: contains=nginx: master process; output=head:3 -->
```bash
docker top web -o pid,args
```

```text
PID                 COMMAND
2569486             nginx: master process nginx -g daemon off;
2569530             nginx: worker process
...
```

Disposable: since it holds no state, replacing it loses nothing. Remove it and start a new one:

<!-- test: retry=10; contains=200 -->
```bash
docker rm -f web > /dev/null
docker run -d --name web -p 8080:80 nginx:1.30-alpine > /dev/null
sleep 1
curl -sI http://localhost:8080/ | head -1
```

## Command breakdown

| Command | What it does |
|---|---|
| `ls -l /var/log/nginx` | shows that the log files are links (`->`) to `/dev/stdout` and `/dev/stderr` |
| `docker logs NAME` | what the container wrote to its standard output and error |
| `docker top NAME -o pid,args` | the processes running in the container, with chosen columns |
| `curl -sI URL \| head -1` | request only the headers and print the status line (`HTTP/1.1 200 OK`) |

## Hands-on lab

**Instructions.** Request a page that does not exist from the `web` container, then find that request in the
container's logs.

**Expected result.** `curl` prints `HTTP/1.1 404 Not Found`, and `docker logs web` contains a line with `"HEAD /missing.html HTTP/1.1" 404`.

**Verification.**

<!-- test: retry=5; contains=404 -->
```bash
curl -sI http://localhost:8080/missing.html | head -1
docker logs web 2>/dev/null | grep missing.html
```

## Break it

A (hypothetical) worker written the "server way": it writes its log to a file inside the container.

<!-- test: contains=lines in docker logs: 0; output -->
```bash
docker run -d --name worker alpine:3.23 sh -c 'while true; do echo "$(date +%T) order processed" >> /var/log/app.log; sleep 1; done' > /dev/null
sleep 3
docker logs worker
echo "lines in docker logs: $(docker logs worker 2>&1 | wc -l | tr -d ' ')"
```

```text
lines in docker logs: 0
```

`docker logs worker` prints nothing: zero lines, although the worker has been working for three seconds.

## Troubleshoot it

The container is running and working: the log exists, but only inside the container's file system:

<!-- test: contains=order processed; output -->
```bash
docker exec worker tail -n 2 /var/log/app.log
```

```text
12:16:44 order processed
12:16:45 order processed
```

Docker (and Kubernetes, and every log collector built on them) only captures a container's **standard output and
error**. A file inside the container is invisible to them, it fills the container's writable layer, and it disappears
with the container (lesson 053). In production, nobody would see this worker's logs.

## Fix it

Write to standard output. When you can change the application, print instead of writing a file; when you cannot, do
what the Nginx image does and point the log file at `/dev/stdout`:

<!-- test: contains=order processed -->
```bash
docker rm -f worker > /dev/null
docker run -d --name worker alpine:3.23 sh -c 'ln -sf /dev/stdout /var/log/app.log; while true; do echo "$(date +%T) order processed" >> /var/log/app.log; sleep 1; done'
sleep 3
docker logs worker | tail -n 2
```

## Practice challenge

The Nginx image also links `error.log` to `/dev/stderr`. Make Nginx write an **error** (not access) log entry, and show
it using only the container's standard error stream.

<details>
<summary>Solution</summary>

A missing file is logged both as a 404 access entry (stdout) and as an `open() … failed` error (stderr). Discard
standard output to see only standard error:

<!-- test: retry=5; contains=No such file or directory; output -->
```bash
curl -s http://localhost:8080/nothing-here.html > /dev/null
docker logs web 2>&1 > /dev/null | grep nothing-here
```

```text
2026/10/05 12:16:50 [error] 33#33: *3 open() "/usr/share/nginx/html/nothing-here.html" failed (2: No such file or directory), client: 172.17.0.1, server: localhost, request: "GET /nothing-here.html HTTP/1.1", host: "localhost:8080"
```

`docker logs` keeps the two streams apart, like the container wrote them: `2>&1 > /dev/null` keeps stderr and drops
stdout.

</details>

## Real-world example

A team moves a legacy Java application into containers and the operations team sees no logs: the application writes
to `/opt/app/logs/server.log`. Rather than adding a log agent to every container, they change the logging
configuration to log to the console (stdout), and the platform's existing log collector picks everything up, with
the container and Pod names attached. The same change also stops containers from filling their disks with log files.

## Recap

- One concern per container; scale and update the parts separately.
- Logs go to stdout/stderr; `docker logs` and log collectors read nothing else.
- Keep state in volumes or external services, so any container can be deleted and recreated.
- Configuration comes from outside the image; SIGTERM must lead to a clean exit (lesson 130).

## Cleanup

<!-- test -->
```bash
docker rm -f web worker > /dev/null
```

Next: [Lesson 132 · Immutable containers](../132-immutable-containers/README.md)
