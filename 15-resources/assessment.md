# Module 15 assessment · Resource management

> Lessons [097](097-cpu-limits/README.md)–[099](099-memory-pressure/README.md) · ⏱ 30 minutes · try every question
> before opening its answer

## Knowledge check

**1. What happens to a container that tries to use more CPU than `--cpus 0.5` allows?**

<details><summary>Answer</summary>

It is throttled: the kernel pauses it for the rest of each 100 ms period once it has used 50 ms. It is never killed
for CPU use (lesson 097).

</details>

**2. What happens to a container that needs more memory than `--memory 64m` allows?**

<details><summary>Answer</summary>

The kernel reclaims what it can, then the OOM killer kills a process in the container with SIGKILL. If it was the main
process, the container exits with code 137 and `OOMKilled=true` (lessons 098, 099).

</details>

**3. Which cgroup files show the CPU and memory limits from inside a container?**

<details><summary>Answer</summary>

`/sys/fs/cgroup/cpu.max` (`50000 100000` for half a core) and `/sys/fs/cgroup/memory.max` (bytes, or `max`)
(lessons 097, 098).

</details>

**4. A container exited with code 137. Was it out of memory?**

<details><summary>Answer</summary>

Not necessarily: 137 means SIGKILL. `docker inspect --format '{{.State.OOMKilled}}'` says whether the OOM killer did
it; `docker kill` or a `docker stop` time-out also produce 137 (lesson 099).

</details>

**5. `docker ps` shows a container `Up`, yet one of its worker processes was killed for memory. Where do you see it?**

<details><summary>Answer</summary>

`docker inspect --format '{{.State.OOMKilled}}'` is `true` although the container runs, `oom_kill` in
`/sys/fs/cgroup/memory.events` inside the container counts the kills, and `docker events` has `oom` events (lesson 099).

</details>

**6. How do you change the memory limit of a running container?**

<details><summary>Answer</summary>

`docker update --memory 256m --memory-swap 256m NAME` (lesson 098).

</details>

**7. What does `--memory-swap` equal to `--memory` mean?**

<details><summary>Answer</summary>

Memory plus swap equals the memory limit: the container gets no swap (lesson 098).

</details>

## Practical task

Start a container named `job` from `alpine:3.23` that sleeps for 300 seconds, with half a CPU core, 96 MB of memory and
no swap. Prove all three limits from inside the container and from `docker inspect`.

<details><summary>Solution</summary>

<!-- test: contains=cpu.max=50000 100000; contains=memory.max=100663296; contains=Memory=100663296 MemorySwap=100663296 NanoCpus=500000000; output -->
```bash
docker run -d --name job --cpus 0.5 --memory 96m --memory-swap 96m alpine:3.23 sleep 300 > /dev/null
docker exec job sh -c 'echo "cpu.max=$(cat /sys/fs/cgroup/cpu.max) memory.max=$(cat /sys/fs/cgroup/memory.max)"'
docker inspect --format 'Memory={{.HostConfig.Memory}} MemorySwap={{.HostConfig.MemorySwap}} NanoCpus={{.HostConfig.NanoCpus}}' job
```

```text
cpu.max=50000 100000 memory.max=100663296
Memory=100663296 MemorySwap=100663296 NanoCpus=500000000
```

</details>

## Troubleshooting task

A nightly import job "just disappears". Reproduce it:

<!-- test: contains=started import -->
```bash
docker run -d --name import --memory 48m --memory-swap 48m python:3.14-alpine \
  python -c 'rows = []
for i in range(40): rows.append(b"r" * 4 * 1024 * 1024); print(f"imported batch {i}", flush=True)' > /dev/null && echo "started import"
```

Find out how it ended, why, and how far it got.

<details><summary>Solution</summary>

<!-- test: retry=15; contains=exit=137 oom=true; output -->
```bash
docker inspect --format 'status={{.State.Status}} exit={{.State.ExitCode}} oom={{.State.OOMKilled}}' import
docker logs import | tail -1
```

```text
status=exited exit=137 oom=true
imported batch 9
```

Exit 137 with `OOMKilled=true`: the kernel killed it at the 48 MB limit. The job keeps every 4 MB batch in memory;
40 batches need 160 MB. Either process batches one at a time (write each one out and drop it) or, if the job really
needs the memory, raise the limit to what it measurably uses.

</details>

## Real-world scenario

Three services share one host: an API, a background worker and a database. During the nightly batch, the worker uses
all CPU cores and the API's response times rise from milliseconds to seconds. Last month, the worker's memory leak got
the database killed by the host's OOM killer. Propose limits and explain them.

<details><summary>Model answer</summary>

Measure each service's normal and peak usage with `docker stats` first. Give the worker a CPU ceiling (`--cpus`) below
the host's core count so the API always has cores left, and a memory limit with headroom over its measured peak, so a
leak kills the **worker** (OOM inside its own cgroup), not the database (lessons 097, 098). Give the database a memory
limit that matches its configured caches, and the API limits from its measurements. Watch `nr_throttled` and `oom`
events after the change: frequent throttling of the API means its limit is too low; OOM kills of the worker mean the
leak must be fixed (lesson 099).

</details>

## Cleanup

<!-- test -->
```bash
docker rm -f job import > /dev/null 2>&1 || true
```
