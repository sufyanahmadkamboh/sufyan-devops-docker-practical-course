# Lesson 098 · Memory limits

> Level 16 · Resource management · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

Memory is different from CPU: CPU can be slowed down, memory cannot be "slowed". When a container reaches its memory
limit, the kernel first reclaims what it can (file caches), and if the container still needs more, the kernel's
**OOM killer** (out of memory) kills a process in it. Without a limit, a leaking container can eat the host's memory
until the kernel starts killing processes of **other** containers, or of the host.

| Flag | Meaning | cgroup file |
|---|---|---|
| `--memory 256m` | hard limit: above it, the OOM killer acts | `memory.max` |
| `--memory-swap 256m` | memory + swap; equal to `--memory` = no swap | `memory.swap.max` |
| `--memory-reservation 128m` | soft limit: memory the kernel reclaims first when the host is short | `memory.low` |

## Visual

```text
  --memory 64m
                                                                ┌─ limit (memory.max = 67108864 bytes)
  usage   ▁▂▃▄▅▆▇█████████████████████████████████████████████████┤
                                       the kernel reclaims caches │ still more needed?
                                                                  ▼
                                                    OOM killer: SIGKILL → exit code 137, OOMKilled=true

  No limit: the same leak grows until the HOST is out of memory, and the kernel may kill anything.
```

## Lab setup

No files are needed: this lesson uses `alpine` containers.

## Demonstration

What the kernel receives for `--memory 64m` (64 × 1024 × 1024 bytes):

<!-- test: contains=67108864; output -->
```bash
docker run --rm --memory 64m alpine:3.23 cat /sys/fs/cgroup/memory.max
```

```text
Unable to find image 'alpine:3.23' locally
3.23: Pulling from library/alpine
d0c1d894c237: Pulling fs layer
d0c1d894c237: Download complete
d0c1d894c237: Pull complete
d836c7fd48f4: Download complete
047d62850641: Download complete
Digest: sha256:85fe1e81d6758c208f3e1eed4338a1997e19d4be002d4dd32d3100c9a8c010a0
Status: Downloaded newer image for alpine:3.23
67108864
```

And without a limit:

<!-- test: contains=max; output -->
```bash
docker run --rm alpine:3.23 cat /sys/fs/cgroup/memory.max
```

```text
max
```

A process that needs 100 MB in a container limited to 32 MB (without swap). `head -c 100m /dev/zero | tail` makes
`tail` hold 100 MB in memory, because `/dev/zero` contains no line breaks:

<!-- test: contains=exit status: 137; output -->
```bash
docker run --name greedy --memory 32m --memory-swap 32m alpine:3.23 sh -c 'head -c 100m /dev/zero | tail' ||
  echo "exit status: $?"
```

```text
Killed
exit status: 137
```

<!-- test: contains=exit=137; output -->
```bash
docker inspect --format 'exit={{.State.ExitCode}} oom={{.State.OOMKilled}}' greedy
docker rm greedy > /dev/null
```

```text
exit=137 oom=true
```

Exit code 137 = 128 + 9: the process was killed with signal 9 (SIGKILL). `OOMKilled=true` says the kernel's OOM killer
did it. The engine sets that flag from a notification of the kernel, and when the container exits in the same instant
it can miss it and show `oom=false`; `Killed` and 137 under a memory limit tell the same story, and the cgroup's own
counters (lesson 099) never miss it. Lesson 099 troubleshoots this in depth.

## Command breakdown

| Command | What it does |
|---|---|
| `--memory 64m` (`-m 64m`) | hard memory limit (`b`, `k`, `m`, `g` units) |
| `--memory-swap 64m` | total memory + swap; same value as `--memory` disables swap |
| `--memory-reservation 32m` | soft limit (`memory.low`) |
| `docker inspect --format '{{.HostConfig.Memory}}'` | the limit in bytes (0 = none) |
| `docker inspect --format '{{.State.OOMKilled}}'` | whether the OOM killer stopped the container |

## Hands-on lab

**Instructions.** Start a container with `--memory 128m --memory-reservation 64m`, and show both values in the
container's cgroup files (`memory.max`, `memory.low`) and in `docker inspect`.

**Expected result.** `134217728` and `67108864` in both places.

**Verification.**

<!-- test: contains=134217728; contains=67108864 -->
```bash
docker run -d --name limited --memory 128m --memory-reservation 64m alpine:3.23 sleep 300 > /dev/null
docker exec limited sh -c 'echo "max=$(cat /sys/fs/cgroup/memory.max) low=$(cat /sys/fs/cgroup/memory.low)"'
docker inspect --format 'Memory={{.HostConfig.Memory}} MemoryReservation={{.HostConfig.MemoryReservation}}' limited
docker rm -f limited > /dev/null
```

## Break it

Make a tiny service even tinier:

<!-- test: fail; contains=Minimum memory limit allowed is 6MB; output -->
```bash
docker run --rm --memory 4m alpine:3.23 true 2>&1
```

```text
docker: Error response from daemon: Minimum memory limit allowed is 6MB

Run 'docker run --help' for more information
```

## Troubleshoot it

The engine refuses the container before it starts: a limit below 6 MB cannot hold even the container's own runtime
overhead. The message names the rule. Other limits are refused the same way, for example a reservation above the
limit:

<!-- test: fail; contains=can not be less than memory reservation; output -->
```bash
docker run --rm --memory 64m --memory-reservation 128m alpine:3.23 true 2>&1
```

```text
docker: Error response from daemon: Minimum memory limit can not be less than memory reservation limit, see usage

Run 'docker run --help' for more information
```

## Fix it

Choose a limit from what the application really uses. Measure it first, without a limit, with `docker stats`
(lesson 095), and add headroom:

<!-- test: contains=MEM; output -->
```bash
docker run -d --name measure nginx:1.30-alpine > /dev/null
sleep 2
docker stats --no-stream --format 'MEM {{.Name}} {{.MemUsage}}' measure
docker rm -f measure > /dev/null
```

```text
MEM measure 11.43MiB / 15.35GiB
```

<!-- test: contains=Memory=67108864 -->
```bash
docker run -d --name web --memory 64m nginx:1.30-alpine > /dev/null
docker inspect --format 'Memory={{.HostConfig.Memory}}' web
```

## Practice challenge

Without restarting it, lower the running `web` container's memory limit to 48 MB, and show the new value inside the
container. (`docker update` needs `--memory-swap` too when the container has swap configured.)

<details>
<summary>Solution</summary>

<!-- test: contains=50331648; output -->
```bash
docker update --memory 48m --memory-swap 48m web > /dev/null
docker exec web cat /sys/fs/cgroup/memory.max
```

```text
50331648
```

48 × 1024 × 1024 = 50331648 bytes. Lowering a limit below the current usage makes the kernel reclaim memory, and
OOM-kill if it cannot: measure first.

</details>

## Real-world example

In Kubernetes, `resources.limits.memory: 256Mi` becomes the same `memory.max` value, and `OOMKilled` appears as the
container's last termination reason. Teams set requests and limits from measured usage (dashboards of the cgroup
numbers over a week) rather than guesses, because a limit that is too low kills healthy pods at peak load, and no limit
lets one leak take down a whole node.

## Recap

- `--memory` is a hard limit enforced by the kernel's OOM killer; `--memory-swap` equal to it disables swap.
- An OOM-killed container exits with 137 (SIGKILL) and `OOMKilled=true`.
- Limits below 6 MB, or reservations above the limit, are refused before the start.
- Measure real usage with `docker stats`, then set a limit with headroom.

## Cleanup

<!-- test -->
```bash
docker rm -f greedy limited measure web > /dev/null 2>&1 || true
```

Next: [Lesson 099 · Memory pressure](../099-memory-pressure/README.md)
