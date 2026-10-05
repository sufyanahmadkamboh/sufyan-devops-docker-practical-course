# Lesson 086 · Resource limits for security

> Level 13 · Container security · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

Containers share the host's CPU, memory, process table and open-file table. Without limits, **one** container, buggy
or compromised, can exhaust them and take every other container and the host down with it: a denial of service from
the inside. Limits turn "the host is down" into "one container failed". This lesson covers the security view and the
limits that are easy to forget: **processes** (`--pids-limit`) and **open files** (`--ulimit nofile`). Module 15 covers
CPU and memory in depth.

## Visual

```text
  Without limits                                        With limits
  ┌──────────────── host ────────────────┐              ┌──────────────── host ────────────────┐
  │ compromised container: fork bomb,    │              │ compromised container                │
  │ memory leak, crypto miner            │              │   --pids-limit 100  → can't fork     │
  │   ▼  takes ALL processes, memory,    │              │   --memory 256m     → OOM-killed     │
  │      CPU of the host                 │              │   --cpus 1          → throttled      │
  │ other containers: starved, killed    │              │ other containers: unaffected         │
  └──────────────────────────────────────┘              └──────────────────────────────────────┘
```

| Flag | Protects against | cgroup / kernel setting |
|---|---|---|
| `--pids-limit 100` | fork bombs, runaway process creation | `pids.max` |
| `--memory 256m` | memory exhaustion (lesson 098) | `memory.max` |
| `--cpus 1` | CPU starvation (lesson 097) | `cpu.max` |
| `--ulimit nofile=1024:1024` | file-descriptor exhaustion | `RLIMIT_NOFILE` |

## Lab setup

No files are needed: this lesson uses `alpine` containers.

## Demonstration

By default, a container may create as many processes as the host allows: `max` (no limit of its own), or a limit
that the host itself sets for its containers:

<!-- test: output -->
```bash
docker run --rm alpine:3.23 cat /sys/fs/cgroup/pids.max
```

```text
max
```

With a limit, the kernel enforces it for the whole container:

<!-- test: contains=10; output -->
```bash
docker run --rm --pids-limit 10 alpine:3.23 cat /sys/fs/cgroup/pids.max
```

```text
10
```

Simulate a runaway process creator (20 background processes; a real fork bomb would try millions) in a container
limited to 10 processes:

<!-- test: contains=can't fork; output -->
```bash
docker run --rm --pids-limit 10 alpine:3.23 sh -c 'for i in $(seq 1 20); do sleep 30 & done; echo "all started"' 2>&1 | tail -1
```

```text
sh: can't fork: Resource temporarily unavailable
```

The container fails on its own; the host and the other containers are not affected.

## Command breakdown

| Command | What it does |
|---|---|
| `--pids-limit N` | at most N processes and threads in the container |
| `--ulimit nofile=SOFT:HARD` | maximum open files per process |
| `--memory`, `--cpus` | memory and CPU ceilings (module 15) |
| `docker stats --no-stream` | current CPU, memory and PIDs per container |
| `docker inspect --format '{{.HostConfig.PidsLimit}}'` | the configured process limit |

## Hands-on lab

**Instructions.** Start a container with `--ulimit nofile=64:64` and show the open-file limit inside it with
`ulimit -n`.

**Expected result.** `64`.

**Verification.**

<!-- test: contains=64 -->
```bash
docker run --rm --ulimit nofile=64:64 alpine:3.23 sh -c 'ulimit -n'
```

## Break it

The same protection with a limit that is too tight for a legitimate application: a web server with worker processes
under `--pids-limit 3`:

<!-- test: contains=started web -->
```bash
docker run -d --name web --pids-limit 3 nginx:1.30-alpine > /dev/null && echo "started web"
```

<!-- test: retry=5; anyof=Resource temporarily unavailable||fork() failed; output -->
```bash
docker logs web 2>&1 | grep -iE 'fork|resource' | head -2
```

```text
/docker-entrypoint.sh: line 8: can't fork: Resource temporarily unavailable
```

## Troubleshoot it

`can't fork: Resource temporarily unavailable` (`EAGAIN`) is the error a process gets when the pids limit is reached.
Here it hit nginx's start script, before nginx itself even ran. Compare the limit with the container's state:

<!-- test: contains=limit=3; output -->
```bash
echo "limit=$(docker inspect --format '{{.HostConfig.PidsLimit}}' web)"
docker ps -a --filter name=web --format 'status={{.Status}}'
```

```text
limit=3
status=Exited (2) Less than a second ago
```

The start script runs helper commands (each one a process), and nginx then starts one worker process per CPU core:
three processes are far too few.

## Fix it

Measure what the application needs without a limit, then set a limit with generous headroom, so it stops runaways
without hurting normal operation:

<!-- test: contains=running=; output -->
```bash
docker rm -f web > /dev/null
docker run -d --name web nginx:1.30-alpine > /dev/null
sleep 2
docker stats --no-stream --format 'running={{.PIDs}}' web
```

```text
running=15
```

<!-- test: contains=started web -->
```bash
docker rm -f web > /dev/null
docker run -d --name web --pids-limit 100 --memory 128m --cpus 1 nginx:1.30-alpine > /dev/null && echo "started web"
```

<!-- test: retry=5; contains=pids=100 memory=134217728 cpus=1000000000 -->
```bash
docker inspect --format 'pids={{.HostConfig.PidsLimit}} memory={{.HostConfig.Memory}} cpus={{.HostConfig.NanoCpus}}' web
```

## Practice challenge

Show that the open-file limit works: in a container with `--ulimit nofile=20:20`, open files until the kernel refuses,
and report how many could be opened.

<details>
<summary>Solution</summary>

<!-- test: contains=Errno 24; output -->
```bash
docker run --rm --ulimit nofile=20:20 python:3.14-alpine python -c '
files = []
try:
    while True:
        files.append(open("/dev/null"))
except OSError as error:
    print(f"opened {len(files)} files, then: {error}")'
```

```text
opened 17 files, then: [Errno 24] No file descriptors available: '/dev/null'
```

With a limit of 20, descriptors 0–19 exist; standard input, output and error already use three of them. A service that
leaks connections or file handles hits the same wall, inside its own container only. Error 24 (`EMFILE`) reads
`No file descriptors available` with Alpine's C library (musl) and `Too many open files` with glibc (Debian, Ubuntu).

</details>

## Real-world example

Kubernetes clusters set a default pids limit per pod on each node (`podPidsLimit` in the kubelet configuration) and
require memory and CPU limits through admission policies, so that a compromised pod mining cryptocurrency or a fork
bomb in one namespace cannot take a node down. Docker hosts get the same protection from `--pids-limit`, `--memory`
and `--cpus` on every container, or the `deploy.resources.limits` section in Compose (lesson 064).

## Recap

- Unlimited containers can exhaust the host's processes, memory and CPU: a denial of service from the inside.
- `--pids-limit` stops fork bombs; `--ulimit nofile` bounds open files; `--memory` and `--cpus` bound the rest.
- "Resource temporarily unavailable" / `fork() failed` = the pids limit was reached.
- Measure normal usage, then set limits with headroom.

## Cleanup

<!-- test -->
```bash
docker rm -f web > /dev/null 2>&1 || true
```

Next: [Lesson 087 · Why multi-stage builds?](../../13-multistage/087-why-multistage/README.md)
