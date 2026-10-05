# Lesson 009 · Container lifecycle

> Level 2 · First container · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

A container moves through states: **created**, **running**, **paused**, **exited**, and finally **removed**. Each
`docker` command moves it from one state to another. The most important transition is **stop**: Docker first asks the
main process to shut down cleanly (a `SIGTERM` signal), waits for a grace period, and only then kills it (`SIGKILL`).
Applications that handle `SIGTERM` finish their work; those that do not are killed and lose it.

## Visual

```text
              docker create                docker start
   (image) ───────────────▶  created  ─────────────────▶  running  ◀──── docker restart
                                                          │  ▲  │
                                           docker pause   │  │  │ docker unpause
                                                          ▼  │  │
                                                         paused │
                                                                │ docker stop  (SIGTERM … grace period … SIGKILL)
                                                                │ docker kill  (SIGKILL at once)
                                                                │ the process ends by itself
                                                                ▼
                                       docker start ◀───  exited (exit code)
                                                                │ docker rm
                                                                ▼
                                                             removed

 docker run = create + start          docker run -d = … in the background (detached)
 docker rm -f = kill + rm             docker run --rm = rm automatically when it exits
```

## Lab setup

No files are needed. A small helper prints a container's state; define it in your terminal for this lesson:

<!-- test: contains=defined -->
```bash
echo 'state() { docker inspect --format "{{.Name}}: {{.State.Status}} (exit code {{.State.ExitCode}})" "$@"; }' > ~/docker-practice-state.sh
echo "helper defined: run  . ~/docker-practice-state.sh  in each new terminal"
```

## Demonstration

Walk an Nginx container through every state:

<!-- test: contains=created; contains=running; contains=paused; output -->
```bash
. ~/docker-practice-state.sh
docker create --name web nginx:1.30-alpine > /dev/null; state web
docker start web > /dev/null;   state web
docker pause web > /dev/null;   state web
docker unpause web > /dev/null; state web
```

```text
/web: created (exit code 0)
/web: running (exit code 0)
/web: paused (exit code 0)
/web: running (exit code 0)
```

Stop it. Nginx handles the stop signal and shuts down cleanly, so it exits with code `0`:

<!-- test: contains=exited (exit code 0); output -->
```bash
. ~/docker-practice-state.sh
docker stop web > /dev/null; state web
docker start web > /dev/null; state web
docker restart web > /dev/null; state web
```

```text
/web: exited (exit code 0)
/web: running (exit code 0)
/web: running (exit code 0)
```

An exited container can be started again: its writable layer is still there. `restart` is stop + start. Now a process
that **ignores** `SIGTERM`: `sleep` running as the container's main process (PID 1). `docker stop` waits for the grace
period, then kills it:

<!-- test: contains=exit code 137; output -->
```bash
. ~/docker-practice-state.sh
docker run -d --name sleeper alpine:3.23 sleep 300 > /dev/null
docker stop -t 2 sleeper > /dev/null; state sleeper
```

```text
/sleeper: exited (exit code 137)
```

Exit code **137** = 128 + 9: the process was killed by signal 9 (`SIGKILL`). Whenever you see 137, the process did not
stop by itself: it was killed by `docker stop` after the grace period, by `docker kill`, or by the kernel for using too
much memory (lesson 098).

## Command breakdown

| Command | Transition |
|---|---|
| `docker create IMAGE` | → created (not running) |
| `docker start NAME` | created/exited → running (`-a` to see its output) |
| `docker run -d IMAGE` | create + start, in the background; prints the container ID |
| `docker pause` / `unpause` | running ⇄ paused (processes frozen, not stopped) |
| `docker stop [-t SECONDS]` | running → exited: `SIGTERM`, wait (`-t`), then `SIGKILL` |
| `docker kill` | running → exited: `SIGKILL` at once (exit code 137) |
| `docker restart` | stop + start |
| `docker rm` / `rm -f` | exited → removed / any state → removed (kills it first) |

## Hands-on lab

**Instructions.** Start `redis:8-alpine` in the background with the name `cache`, stop it, and check its exit code.
Then start the same container again and remove it while it runs, in one command.

**Expected result.** Redis handles `SIGTERM` and saves its data, so it exits with code `0`. `docker rm -f` removes the
running container.

**Verification.**

<!-- test: contains=exit code 0; contains=removed -->
```bash
. ~/docker-practice-state.sh
docker run -d --name cache redis:8-alpine > /dev/null
docker stop cache > /dev/null; state cache
docker start cache > /dev/null
docker rm -f cache > /dev/null && echo "cache removed"
```

## Break it

Remove a container that is still running:

<!-- test: fail; contains=container is running; output -->
```bash
docker rm web
```

```text
Error response from daemon: cannot remove container "web": container is running: stop the container before removing or force remove
```

## Troubleshoot it

`cannot remove container "web": container is running: stop the container before removing or force remove`. Docker
protects running containers from an accidental `rm`. Confirm the state:

<!-- test: contains=running -->
```bash
. ~/docker-practice-state.sh
state web
```

## Fix it

Stop it cleanly, then remove it (or, when you do not care about a clean shutdown, `docker rm -f web`):

<!-- test: contains=web -->
```bash
docker stop web
docker rm web
```

## Practice challenge

A container's main process fails at once with exit code 1. Start it with the restart policy `--restart on-failure:3`, so
that Docker restarts it at most three times, and show how many restarts Docker made.

<details>
<summary>Solution</summary>

<!-- test -->
```bash
docker run -d --name flaky --restart on-failure:3 alpine:3.23 sh -c 'echo starting; exit 1'
```

Wait a few seconds, then:

<!-- test: contains=restarts: 3, status: exited; retry=10; output -->
```bash
docker inspect --format 'restarts: {{.RestartCount}}, status: {{.State.Status}}, exit code: {{.State.ExitCode}}' flaky
```

```text
restarts: 3, status: exited, exit code: 1
```

Docker restarted it three times (waiting a little longer each time), then gave up: the container stays `exited` with
code 1. `docker logs flaky` shows `starting` four times. Other policies: `no` (default), `always`, `unless-stopped`
(lesson 131).

</details>

## Real-world example

During a deployment, the old container receives `SIGTERM`. A well-behaved API stops accepting new requests, finishes the
ones in flight and closes its database connections before the grace period ends. An API that ignores the signal is
killed with 137 after the grace period, and users see failed requests. Kubernetes works the same way (with
`terminationGracePeriodSeconds`), so handling `SIGTERM` is part of making any containerised app production-ready.

## Recap

- States: created → running ⇄ paused → exited → removed; `run` = create + start.
- `stop` sends `SIGTERM`, waits, then `SIGKILL`; `kill` sends `SIGKILL` at once.
- Exit code 137 means the process was killed, not that it finished.
- A running container cannot be removed without `-f`; restart policies restart failed containers.

## Cleanup

<!-- test -->
```bash
docker rm -f web sleeper flaky > /dev/null 2>&1 || true
rm -f ~/docker-practice-state.sh
```

Next: [Lesson 010 · Container names](../010-container-names/README.md)
