# Lesson 099 · Memory pressure and OOM kills

> Level 16 · Resource management · ⏱ 30 minutes · run every command from the course folder

## What are we learning?

How to recognise and investigate a container that runs out of memory. The signs differ depending on **which**
process the kernel kills:

- the container's main process (PID 1): the container stops, exit code **137**, `OOMKilled=true`;
- a child process (a worker under a process manager, a script started by a shell): the container keeps running and
  `docker ps` shows `Up`. Docker still sets `OOMKilled=true`, but only `docker inspect`, Docker's `oom` event and the
  kernel's counters reveal it.

Exit code 137 on its own only means "killed with SIGKILL": `docker kill` and a `docker stop` time-out produce it too.

## Visual

```text
                              container stops?   exit code   OOMKilled   docker events   memory.events oom_kill
  PID 1 killed by OOM         yes                137         true        oom, die        1
  child killed by OOM         no (still Up)      -           true        oom             1   ◀── easy to miss
  docker kill / stop timeout  yes                137         false       kill, die       0

  Investigation:  docker inspect (State) → docker events --filter event=oom → docker stats (usage vs limit)
                  → docker logs (what was happening) → cat /sys/fs/cgroup/memory.events (inside)
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-099 15-resources/099-memory-pressure/examples
cd ~/docker-practice/lesson-099
head -4 leak.py
```

`leak.py` is a cache with a bug: it keeps every 8 MB entry forever. `MAX_ENTRIES` bounds it (the fix).

## Demonstration

Run the leaking cache as the container's main process, with a 64 MB limit and no swap:

<!-- test: contains=started cache -->
```bash
docker run -d --name cache --memory 64m --memory-swap 64m -v "$(pwd)/leak.py:/leak.py:ro" python:3.14-alpine python /leak.py > /dev/null && echo "started cache"
```

<!-- test: retry=15; contains=exit=137 oom=true; output -->
```bash
docker inspect --format 'status={{.State.Status}} exit={{.State.ExitCode}} oom={{.State.OOMKilled}}' cache
```

```text
status=exited exit=137 oom=true
```

The logs show how far it got before the kill (the last line it printed):

<!-- test: contains=cache holds; output -->
```bash
docker logs cache | tail -2
```

```text
cache holds 48 MB
cache holds 56 MB
```

Compare with a container that is killed by hand: same exit code, but not an OOM kill:

<!-- test: contains=exit=137 oom=false; output -->
```bash
docker run -d --name killed alpine:3.23 sleep 300 > /dev/null
docker kill killed > /dev/null
docker inspect --format 'exit={{.State.ExitCode}} oom={{.State.OOMKilled}}' killed
```

```text
exit=137 oom=false
```

## Command breakdown

| Command | What it tells you |
|---|---|
| `docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}'` | 137 + true: the main process was OOM-killed; running + true: a child was |
| `docker events --filter event=oom` | every OOM kill in the container, main process or not |
| `cat /sys/fs/cgroup/memory.events` (inside) | `oom_kill N`: how many processes the kernel killed |
| `docker stats --no-stream` | usage vs limit right now |
| `docker inspect --format '{{.HostConfig.Memory}}'` | the limit in bytes |

## Hands-on lab

**Instructions.** Use `docker events` to list the OOM events of the `cache` container from the last few minutes.

**Expected result.** At least one line `oom`, followed by `die`.

**Verification.**

<!-- test: contains=oom -->
```bash
docker events --since 5m --until "$(date +%s)" --filter container=cache --format '{{.Action}}' | grep -E '^(oom|die)'
```

## Break it

In real services the application often runs **under** another process: a shell script, a process manager, a web
server with worker processes. Run the same cache as a child of a shell that keeps the container alive:

<!-- test: contains=started service -->
```bash
docker run -d --name service --memory 64m --memory-swap 64m -v "$(pwd)/leak.py:/leak.py:ro" python:3.14-alpine \
  sh -c 'python /leak.py; echo "worker exited with status $?"; sleep 300' > /dev/null && echo "started service"
```

<!-- test: retry=15; contains=worker exited with status 137 -->
```bash
docker logs service | tail -1
```

The container is up, the cache is gone:

<!-- test: contains=status=running exit=0 oom=true; output -->
```bash
docker inspect --format 'status={{.State.Status}} exit={{.State.ExitCode}} oom={{.State.OOMKilled}}' service
```

```text
status=running exit=0 oom=true
```

## Troubleshoot it

A **running** container with `OOMKilled=true`: the main process (the shell) survived, a process under it was killed.
`docker ps` shows nothing unusual, so this is easy to miss. The kernel's counters for the container's cgroup include
every process in it:

<!-- test: contains=oom_kill 1; output -->
```bash
docker exec service cat /sys/fs/cgroup/memory.events
```

```text
low 0
high 0
max 35
oom 1
oom_kill 1
oom_group_kill 0
```

And the engine recorded the event:

<!-- test: contains=oom; output -->
```bash
docker events --since 5m --until "$(date +%s)" --filter container=service --filter event=oom --format '{{.Action}} in {{.Actor.Attributes.name}}'
```

```text
oom in service
```

The root cause is in the logs: memory grew steadily, 8 MB at a time, until the limit. A steady climb means a leak
(more memory will only delay the kill); a jump at a particular request means one operation needs more than the limit.

## Fix it

Fix the leak: bound the cache. With at most 4 entries (32 MB) the service runs indefinitely within its 64 MB limit:

<!-- test: contains=started service -->
```bash
docker rm -f service > /dev/null
docker run -d --name service --memory 64m --memory-swap 64m -e MAX_ENTRIES=4 -v "$(pwd)/leak.py:/leak.py:ro" python:3.14-alpine \
  sh -c 'python /leak.py; echo "worker exited with status $?"; sleep 300' > /dev/null && echo "started service"
```

<!-- test: contains=cache holds 32 MB; contains=oom_kill 0; output -->
```bash
sleep 6
docker logs service | tail -1
docker exec service grep oom_kill /sys/fs/cgroup/memory.events
docker stats --no-stream --format '{{.Name}} {{.MemUsage}}' service
```

```text
cache holds 32 MB
oom_kill 0
service 36.16MiB / 64MiB
```

## Practice challenge

Write a short script that reports, for every container on the host (running or stopped), whether its main process was
OOM-killed, and how many OOM kills its running processes have suffered according to `memory.events`.

<details>
<summary>Solution</summary>

<!-- test: contains=/cache oom=true; output -->
```bash
for id in $(docker ps -aq); do
  name=$(docker inspect --format '{{.Name}}' "$id")
  oom=$(docker inspect --format '{{.State.OOMKilled}}' "$id")
  kills=$(docker exec "$id" sh -c 'grep oom_kill /sys/fs/cgroup/memory.events' 2>/dev/null | head -1)
  echo "$name oom=$oom ${kills:-(not running)}"
done
```

```text
/service oom=false oom_kill 0
/killed oom=false (not running)
/cache oom=true (not running)
```

`docker exec` only works on running containers; for stopped ones, `OOMKilled` and the `oom` events are what remains.
`oom=true` on a running container means one of its child processes was killed.

</details>

## Real-world example

A Python API runs under Gunicorn with four worker processes. After a release, users see occasional `502 Bad Gateway`
errors, but `docker ps` shows the container `Up` and it never restarts. Its `OOMKilled` flag, the `oom` events and
the `oom_kill` counter show
workers being killed several times an hour; Gunicorn quietly starts new ones. The new release loads a whole report
into memory per request: streaming it fixed the problem, where doubling the limit would only have made it rarer.

## Recap

- 137 = SIGKILL. `OOMKilled=true` with exit 137: the main process was OOM-killed; `docker kill` gives 137 without it.
- OOM kills of child processes leave the container `Up`: check `OOMKilled`, `memory.events` and
  `docker events --filter event=oom`.
- Logs and `docker stats` show the growth pattern: steady climb = leak, sudden jump = one large operation.
- Fix the memory use first; raise the limit only when the application legitimately needs more.

## Cleanup

<!-- test -->
```bash
docker rm -f cache killed service > /dev/null 2>&1 || true
cd ~ && rm -rf ~/docker-practice/lesson-099
```

Next: [Lesson 100 · Metadata and docker inspect](../../16-advanced/100-metadata-and-inspect/README.md)
