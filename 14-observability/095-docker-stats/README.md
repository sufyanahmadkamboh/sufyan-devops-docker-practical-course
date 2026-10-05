# Lesson 095 · docker stats

> Level 15 · Observability · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

`docker stats` shows, for every running container, how much CPU, memory, network and disk I/O it uses right now, and
how many processes it runs. It reads the numbers from the kernel's **cgroups**, the same mechanism that enforces the
limits of lessons 097–099. When a host is slow, `docker stats` answers the first question: **which container** is it?

## Visual

```text
  docker stats --no-stream

  NAME     CPU %    MEM USAGE / LIMIT     MEM %   NET I/O        BLOCK I/O   PIDS
  web      0.00%    9.1MiB / 15.4GiB      0.06%   1.2kB / 0B     0B / 4kB    15
  worker   99.87%   1.2MiB / 15.4GiB      0.01%   872B / 0B      0B / 0B     2     ◀── the busy one
  cache    0.21%    3.4MiB / 64MiB        5.31%   1kB / 0B       0B / 0B     6     ◀── limited to 64 MiB
            │            │       │                                                  │
            │            │       └ the container's memory limit (or the whole engine's memory)
            │            └ memory the container uses now
            └ 100% = one full CPU core (a container can use more than 100% on several cores)
```

## Lab setup

No files are needed: this lesson uses `nginx` and `alpine` containers.

## Demonstration

Start an idle web server and a small cache with a memory limit:

<!-- test: contains=started -->
```bash
docker run -d --name web nginx:1.30-alpine > /dev/null
docker run -d --name cache --memory 64m redis:8-alpine redis-server --enable-debug-command local > /dev/null
echo "started web and cache"
```

One snapshot (without `--no-stream`, `docker stats` refreshes every second until Ctrl+C):

<!-- test: contains=cache; contains=64MiB; output -->
```bash
docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.PIDs}}' web cache
```

```text
NAME      CPU %     MEM USAGE / LIMIT     PIDS
web       0.00%     11.47MiB / 15.35GiB   15
cache     0.23%     5.637MiB / 64MiB      6
```

The `cache` container's memory limit is the 64 MiB you set; `web` has no limit, so its limit is the memory of the
whole Docker engine (on Docker Desktop, its VM).

## Command breakdown

| Command / placeholder | What it shows |
|---|---|
| `docker stats` | live usage of all running containers (Ctrl+C to stop) |
| `--no-stream` | one snapshot, then exit (for scripts) |
| `--format 'table {{.Name}}\t{{.CPUPerc}}…'` | chosen columns; `.MemPerc`, `.NetIO`, `.BlockIO`, `.PIDs` exist too |
| `docker stats NAME …` | only these containers |
| `docker top NAME` | the processes inside one container |
| `docker update --cpus 0.5 NAME` | change a running container's CPU limit without restarting it |

## Hands-on lab

**Instructions.** Print one snapshot with only the name and memory percentage of every running container, sorted by
memory percentage, highest first.

**Expected result.** Two lines, `cache` and `web`, each with a percentage.

**Verification.**

<!-- test: contains=cache; contains=web -->
```bash
docker stats --no-stream --format '{{.MemPerc}} {{.Name}}' | sort -rn
```

## Break it

Somebody starts a "worker" with a bug: an endless loop that never sleeps.

<!-- test: contains=started worker -->
```bash
docker run -d --name worker alpine:3.23 sh -c 'while :; do :; done' > /dev/null && echo "started worker"
```

Everything on the host gets slower. Which container is it?

## Troubleshoot it

Take a snapshot and sort by CPU (give the worker a few seconds to show up in the measurement):

<!-- test: retry=5; contains=worker; output -->
```bash
sleep 3
docker stats --no-stream --format '{{.CPUPerc}} {{.Name}}' | sort -rn | head -1
```

```text
99.80% worker
```

About 100%: one full CPU core, all the time. Look inside it:

<!-- test: contains=while; output -->
```bash
docker top worker -o pid,args
```

```text
PID                 COMMAND
2622829             sh -c while :; do :; done
```

The loop has no pause and no work: it is a bug, not load.

## Fix it

Two steps, as in a real incident. **Contain** it immediately with a CPU limit, without restarting it (lesson 097):

<!-- test: contains=worker -->
```bash
docker update --cpus 0.2 worker
```

<!-- test: retry=5; contains=worker; output -->
```bash
sleep 3
docker stats --no-stream --format '{{.CPUPerc}} {{.Name}}' worker
```

```text
20.07% worker
```

The worker now gets at most a fifth of a core: the host is fine again. Then **fix the cause** (the code) and replace
the container:

<!-- test: contains=worker -->
```bash
docker rm -f worker > /dev/null
docker run -d --name worker --cpus 0.5 alpine:3.23 sh -c 'while :; do sleep 1; done' > /dev/null
docker stats --no-stream --format '{{.CPUPerc}} {{.Name}}' worker
```

## Practice challenge

Write a command that prints a warning for every running container that uses more than 50% of its memory limit. Test it
by filling the `cache` container's memory: `docker exec cache redis-cli DEBUG POPULATE 550000` writes 550,000
test keys (the `cache` container was started with `--enable-debug-command local` to allow it).

<details>
<summary>Solution</summary>

<!-- test: contains=OK -->
```bash
docker exec cache redis-cli DEBUG POPULATE 550000
```

<!-- test: contains=WARNING cache; output -->
```bash
docker stats --no-stream --format '{{.Name}} {{.MemPerc}}' | tr -d '%' |
  awk '$2 > 50 { print "WARNING " $1 " uses " $2 "% of its memory limit" }'
```

```text
WARNING cache uses 64.40% of its memory limit
```

`tr -d '%'` removes the percent sign so `awk` can compare numbers. Monitoring systems (cAdvisor + Prometheus, the
Docker integration of Datadog and others) collect the same cgroup numbers continuously and alert on rules like this.

</details>

## Real-world example

An on-call engineer is paged because a build server is slow. `docker stats --no-stream` shows one CI job's container
at several hundred percent CPU and near its memory limit, while the others are idle. `docker top` reveals a test suite
stuck in a retry loop. The engineer stops that container, the other jobs recover, and the team adds `--cpus` and
`--memory` limits to every CI job so one job can never starve the others again.

## Recap

- `docker stats` shows per-container CPU, memory (usage / limit), network, disk I/O and process count.
- `--no-stream` and `--format` make it scriptable; `sort` finds the top consumer.
- CPU 100% = one full core; the memory limit column shows the container's limit, or the engine's memory.
- Contain with `docker update --cpus/--memory`, then fix the cause.

## Cleanup

<!-- test -->
```bash
docker rm -f web cache worker > /dev/null 2>&1 || true
```

Next: [Lesson 096 · docker events](../096-docker-events/README.md)
