# Lesson 097 · CPU limits

> Level 16 · Resource management · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

Without limits, one container can use every CPU core of the host and slow down everything else. Docker offers three
controls, all enforced by the kernel's **cgroups**:

- `--cpus 1.5`: a hard ceiling, at most one and a half cores' worth of CPU time (the usual choice),
- `--cpuset-cpus 0,1`: run only on these cores,
- `--cpu-shares 512`: a relative weight that matters only when containers compete (default 1024).

## Visual

```text
  --cpus 0.5  →  cgroup cpu.max = "50000 100000"
                  in every 100 ms period the container may run for 50 ms (summed over all its threads)

  period:  |──────────── 100 ms ────────────|──────────── 100 ms ────────────|
  CPU:     ███████████████░░░░░░░░░░░░░░░░░ ███████████████░░░░░░░░░░░░░░░░░
           runs 50 ms      throttled 50 ms   runs 50 ms      throttled 50 ms

  docker stats CPU % → about 50%          the application is not killed, only slowed down
```

## Lab setup

No files are needed: this lesson uses `alpine` containers.

## Demonstration

What the kernel receives for `--cpus 0.5`:

<!-- test: contains=50000 100000; output -->
```bash
docker run --rm --cpus 0.5 alpine:3.23 cat /sys/fs/cgroup/cpu.max
```

```text
50000 100000
```

`max 100000` (no limit) without the flag:

<!-- test: contains=max 100000 -->
```bash
docker run --rm alpine:3.23 cat /sys/fs/cgroup/cpu.max
```

Now a busy loop with that limit. Measure its CPU usage after a few seconds:

<!-- test: contains=started burner -->
```bash
docker run -d --name burner --cpus 0.5 alpine:3.23 sh -c 'while :; do :; done' > /dev/null && echo "started burner"
```

<!-- test: retry=5; contains=burner; output -->
```bash
sleep 3
docker stats --no-stream --format '{{.Name}} {{.CPUPerc}}' burner
```

```text
burner 49.51%
```

The loop would take a whole core; the limit holds it at about half. The kernel counts how often it had to stop the
container:

<!-- test: contains=nr_throttled; output -->
```bash
docker exec burner sh -c 'grep -E "nr_periods|nr_throttled" /sys/fs/cgroup/cpu.stat'
```

```text
nr_periods 48
nr_throttled 46
```

## Command breakdown

| Flag | Effect | cgroup file |
|---|---|---|
| `--cpus 0.5` | at most half a core of CPU time | `cpu.max` = `50000 100000` |
| `--cpuset-cpus 0,1` | only on cores 0 and 1 | `cpuset.cpus.effective` |
| `--cpu-shares 512` | half the default weight when CPUs are contended | `cpu.weight` |
| `docker update --cpus 1 NAME` | change the limit of a running container | |
| `docker inspect --format '{{.HostConfig.NanoCpus}}'` | the limit in billionths of a core | |

## Hands-on lab

**Instructions.** Start a container pinned to core 0 only and show which cores it may use.

**Expected result.** `0`.

**Verification.**

<!-- test: contains=0 -->
```bash
docker run --rm --cpuset-cpus 0 alpine:3.23 cat /sys/fs/cgroup/cpuset.cpus.effective
```

## Break it

A teammate copies a production setting to their laptop:

<!-- test: fail; contains=range of CPUs is from 0.01; output -->
```bash
docker run --rm --cpus 64 alpine:3.23 true 2>&1
```

```text
docker: Error response from daemon: range of CPUs is from 0.01 to 14.00, as there are only 14 CPUs available

Run 'docker run --help' for more information
```

## Troubleshoot it

The engine refuses limits it cannot provide, and says what is possible: from 0.01 to the number of CPUs the engine
has. Ask the engine how many it has (on Docker Desktop, the VM's CPUs, configurable in its settings):

<!-- test: contains=CPUs; output -->
```bash
echo "engine CPUs: $(docker info --format '{{.NCPU}}')"
```

```text
engine CPUs: 14
```

## Fix it

Use a limit within that range. A portable choice for development is a fraction of what the machine has:

<!-- test: contains=cpu.max; output -->
```bash
docker run --rm --cpus 1 alpine:3.23 sh -c 'echo "cpu.max: $(cat /sys/fs/cgroup/cpu.max)"'
```

```text
cpu.max: 100000 100000
```

## Practice challenge

`burner` is running with `--cpus 0.5`. Raise its limit to `1.0` without restarting it, prove that the new limit is
active inside the container, and check that it now uses about one full core.

<details>
<summary>Solution</summary>

<!-- test: contains=100000 100000; output -->
```bash
docker update --cpus 1 burner > /dev/null
docker exec burner cat /sys/fs/cgroup/cpu.max
```

```text
100000 100000
```

<!-- test: retry=5; contains=burner; output -->
```bash
sleep 3
docker stats --no-stream --format '{{.Name}} {{.CPUPerc}}' burner
```

```text
burner 100.32%
```

`docker update` rewrites the container's cgroup settings while it runs: useful to contain a runaway container during
an incident (lesson 095).

</details>

## Real-world example

On a shared CI host, every job container gets `--cpus 2`, so a job with a runaway test cannot starve the other jobs.
Kubernetes uses the same cgroup setting for a container's `resources.limits.cpu: "500m"` (500 millicores = 0.5). A
limit that is too low shows up as **throttling**: requests become slow although the CPU usage looks moderate;
`nr_throttled` in `cpu.stat` reveals it (troubleshooting problem 23).

## Recap

- `--cpus N` sets a hard ceiling of N cores' worth of CPU time (cgroup `cpu.max`).
- A limited container is throttled (slowed down), never killed, for using too much CPU.
- `--cpuset-cpus` pins to cores; `--cpu-shares` only weights containers against each other under contention.
- `docker update --cpus` changes the limit of a running container.

## Cleanup

<!-- test -->
```bash
docker rm -f burner > /dev/null 2>&1 || true
```

Next: [Lesson 098 · Memory limits](../098-memory-limits/README.md)
