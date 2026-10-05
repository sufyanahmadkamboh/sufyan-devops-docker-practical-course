# Troubleshooting problem 22 · Memory limit exceeded

> ⏱ 15 minutes · run every command from the course folder · related lessons: 096, 098, 099

## Problem

The nightly report job got a memory limit of 64 MB during a cost review. Since then it dies without a single error
message, every night, with exit code 137.

## Symptoms

The job (a Python one-liner standing in for the report: it loads 150 MB of data) runs with the new limit:

<!-- test -->
```bash
docker run -d --name report -m 64m --memory-swap 64m python:3.14-alpine \
  python -c "data = bytearray(150 * 1024 * 1024); print('report built')" > /dev/null
```

<!-- test: retry=10; contains=Exited (137); output -->
```bash
docker ps -a --filter name=report --format '{{.Names}}: {{.Status}}'
```

```text
report: Exited (137) 2 seconds ago
```

<!-- test: absent=report built; output -->
```bash
echo "logs: [$(docker logs report 2>&1)]"
```

```text
logs: []
```

## Investigation

**1. Who ended the process?** Exit code 137 is 128 + 9: the process was killed with signal 9 (`SIGKILL`). It did not
exit by itself, so it could not log anything:

<!-- test: contains=OOMKilled: true; output -->
```bash
docker inspect --format 'exit code: {{.State.ExitCode}}, OOMKilled: {{.State.OOMKilled}}, memory limit: {{.HostConfig.Memory}} bytes' report
```

```text
exit code: 137, OOMKilled: true, memory limit: 67108864 bytes
```

**2. The engine recorded it as an event** (lesson 096):

<!-- test: contains=oom; output -->
```bash
docker events --since 5m --until 0s --filter container=report --filter event=oom --format '{{.Time}} {{.Action}} {{.Actor.Attributes.name}}' | cut -d' ' -f2-
```

```text
oom report
```

**3. How much does the job need?** Run it once with a generous limit and watch its peak (`docker stats` for a
service; for a short job, the kernel's peak counter of the container's cgroup):

<!-- test: contains=peak memory; output -->
```bash
docker run --rm -m 512m python:3.14-alpine python -c "data = bytearray(150 * 1024 * 1024); print('peak memory:', int(open('/sys/fs/cgroup/memory.peak').read()) // 2**20, 'MB')"
```

```text
peak memory: 154 MB
```

## Commands

| Command | What it tells you |
|---|---|
| `docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}' NAME` | 137 + `true` = killed by the kernel's out-of-memory killer |
| `docker inspect --format '{{.HostConfig.Memory}}' NAME` | the limit in bytes (0 = none) |
| `docker events --filter event=oom` | every out-of-memory kill, with the container name |
| `docker stats --no-stream` | the live usage and limit of running containers (lesson 095) |
| `cat /sys/fs/cgroup/memory.peak` (inside) | the highest usage so far (cgroup v2) |

## Output interpretation

| Exit code | OOMKilled | Meaning |
|---|---|---|
| 137 | `true` | the container exceeded its memory limit and the kernel killed it |
| 137 | `false` | something sent `SIGKILL`: `docker kill`, or `docker stop` after its timeout |
| 143 | `false` | `SIGTERM`: a normal `docker stop` the process obeyed |

Empty logs are typical: `SIGKILL` cannot be caught, so the application gets no chance to report anything.

## Root cause

The job needs more than 150 MB at its peak; the new limit is 64 MB. The kernel kills it as soon as it crosses the
limit.

## Fix

Set the limit from the measured peak plus headroom (or make the job use less memory, for example by streaming the data
instead of loading it at once):

<!-- test -->
```bash
docker rm report > /dev/null
docker run -d --name report -m 256m --memory-swap 256m python:3.14-alpine \
  python -c "data = bytearray(150 * 1024 * 1024); print('report built')" > /dev/null
```

## Verification

<!-- test: retry=10; contains=Exited (0); contains=report built; output -->
```bash
docker ps -a --filter name=report --format '{{.Names}}: {{.Status}}'
docker logs report
docker inspect --format 'OOMKilled: {{.State.OOMKilled}}' report
```

```text
report: Exited (0) 2 seconds ago
report built
OOMKilled: false
```

## Prevention

- Measure before you limit: `docker stats` under realistic load, the cgroup's `memory.peak` for jobs (lesson 098).
- Alert on `oom` events and on exit code 137 in your monitoring; a restart policy alone only hides the kills.
- Runtimes with their own heap settings must be sized inside the limit: Java `-XX:MaxRAMPercentage`, Node.js
  `--max-old-space-size` (lesson 099).

## Cleanup

<!-- test -->
```bash
docker rm -f report > /dev/null
```

Next: [Problem 23 · CPU throttling](../23-cpu-throttling/README.md)
