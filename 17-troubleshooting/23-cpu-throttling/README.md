# Troubleshooting problem 23 · CPU throttling

> ⏱ 15 minutes · run every command from the course folder · related lessons: 095, 097

## Problem

The thumbnail service became several times slower after its deployment configuration got `--cpus 0.25`. There are no
errors and the server has idle CPU cores, but every job takes longer.

## Symptoms

The service, with the limit (a Python container that runs the CPU-heavy job on request):

<!-- test -->
```bash
docker run -d --name thumbs --cpus 0.25 python:3.14-alpine sleep 3600 > /dev/null
```

<!-- test: contains=job took; output -->
```bash
docker exec thumbs python -c "import time; t = time.time(); sum(i * i for i in range(5_000_000)); print(f'job took {time.time() - t:.1f} s')"
```

```text
job took 1.3 s
```

## Investigation

**1. Which limit is configured?** `NanoCpus` is the `--cpus` value in billionths of a CPU:

<!-- test: contains=0.25 CPU; output -->
```bash
docker inspect --format '{{.HostConfig.NanoCpus}}' thumbs | awk '{print "limit:", $1 / 1e9, "CPU"}'
```

```text
limit: 0.25 CPU
```

**2. Was the container throttled?** The kernel counts it in the container's cgroup:

<!-- test: contains=nr_throttled; output -->
```bash
docker exec thumbs cat /sys/fs/cgroup/cpu.max
docker exec thumbs grep -E 'nr_periods|nr_throttled|throttled_usec' /sys/fs/cgroup/cpu.stat
```

```text
25000 100000
nr_periods 21
nr_throttled 14
throttled_usec 1039138
```

**3. What does `docker stats` show under load?** Start a busy loop in the background and look:

<!-- test: contains=thumbs; output -->
```bash
docker exec -d thumbs python -c "while True: pass"
sleep 3
docker stats --no-stream --format '{{.Name}}: CPU {{.CPUPerc}}' thumbs
docker exec thumbs pkill -f "while True"
```

```text
thumbs: CPU 25.40%
```

## Commands

| Command | What it tells you |
|---|---|
| `docker inspect --format '{{.HostConfig.NanoCpus}} {{.HostConfig.CpuQuota}}' NAME` | the CPU limit |
| `docker exec NAME cat /sys/fs/cgroup/cpu.max` | quota and period: `25000 100000` = 25 ms of CPU per 100 ms |
| `docker exec NAME cat /sys/fs/cgroup/cpu.stat` | `nr_throttled` (periods in which it was stopped) and `throttled_usec` (time lost) |
| `docker stats --no-stream` | the usage: it never goes above the limit (here 25 %) |

## Output interpretation

`cpu.max` `25000 100000`: in every 100 ms period the container may use 25 ms of CPU time. A CPU-heavy job uses its
25 ms early in each period and is then **stopped** until the next period starts; `nr_throttled` counts those periods
and `throttled_usec` the time lost. `docker stats` stays at about 25 % however idle the server is. Throttling is not an
error and is not logged: it only shows as slowness and as latency in requests.

## Root cause

The limit of a quarter of a CPU is far below what the job needs to finish in time.

## Fix

Limits can be changed on a running container with `docker update` (Compose: `deploy.resources.limits.cpus`):

<!-- test: contains=thumbs -->
```bash
docker update --cpus 1 thumbs
```

## Verification

<!-- test: contains=job took; contains=100000 100000; output -->
```bash
docker exec thumbs cat /sys/fs/cgroup/cpu.max
docker exec thumbs python -c "import time; t = time.time(); sum(i * i for i in range(5_000_000)); print(f'job took {time.time() - t:.1f} s')"
```

```text
100000 100000
job took 0.3 s
```

The same job, the same machine: a fraction of the time it took with 0.25 CPU (your numbers depend on your CPU).

## Prevention

- Size CPU limits from measurements under realistic load (`docker stats`, `cpu.stat`), and recheck after code changes.
- Watch throttling, not only usage: `throttled_usec` growing is the signal; monitoring systems export it per container.
- For latency-sensitive services, prefer a generous limit or CPU shares (`--cpu-shares`), which only matter when the
  host is busy (lesson 097).
- Multi-threaded runtimes size their thread pools from the CPU limit (Java, .NET, Go's `GOMAXPROCS` in recent
  versions): a tiny limit can also mean fewer worker threads.

## Cleanup

<!-- test -->
```bash
docker rm -f thumbs > /dev/null
```

Next: [Problem 24 · Registry authentication failure](../24-registry-authentication-failure/README.md)
