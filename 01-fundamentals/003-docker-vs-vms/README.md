# Lesson 003 · Docker vs virtual machines

> Level 1 · Container fundamentals · ⏱ 15 minutes · run every command from the course folder

## What are we learning?

A **virtual machine** emulates a whole computer: a hypervisor runs a complete guest operating system, with its own
kernel, for each VM. A **container** is an isolated process on the host's kernel: it brings its own files (libraries,
runtime, application) but shares the kernel with every other container. That one difference explains everything else:
containers start in under a second, weigh megabytes instead of gigabytes, and are isolated less strongly than VMs.

## Visual

```text
          Virtual machines                                 Containers

 ┌────────────┐ ┌────────────┐ ┌────────────┐     ┌──────────┐ ┌──────────┐ ┌──────────┐
 │   App A    │ │   App B    │ │   App C    │     │  App A   │ │  App B   │ │  App C   │
 │ Libraries  │ │ Libraries  │ │ Libraries  │     │ Libraries│ │ Libraries│ │ Libraries│
 │ Guest OS + │ │ Guest OS + │ │ Guest OS + │     └──────────┘ └──────────┘ └──────────┘
 │  kernel    │ │  kernel    │ │  kernel    │     ┌──────────────────────────────────────┐
 └────────────┘ └────────────┘ └────────────┘     │       Container engine (Docker)      │
 ┌──────────────────────────────────────────┐     ├──────────────────────────────────────┤
 │              Hypervisor                  │     │      Host OS + ONE shared kernel     │
 ├──────────────────────────────────────────┤     ├──────────────────────────────────────┤
 │              Hardware                    │     │              Hardware                │
 └──────────────────────────────────────────┘     └──────────────────────────────────────┘
   boots in minutes · GBs per VM                     starts in < 1 s · MBs per image
   strong isolation (separate kernels)               process isolation (shared kernel)
```

| | Virtual machine | Container |
|---|---|---|
| Isolates | a whole computer | a process (namespaces + cgroups) |
| Kernel | its own, per VM | the host's, shared |
| Size | gigabytes (full OS) | megabytes (only the files the app needs) |
| Start time | tens of seconds to minutes | well under a second |
| Typical use | different OSes, strong tenant isolation | packaging and running applications |

## Lab setup

No files are needed: this lesson inspects containers directly.

## Demonstration

Ask the Docker engine which kernel it runs, then ask two containers from **different** distributions (Alpine and Debian):

<!-- test: contains=same kernel; output -->
```bash
engine=$(docker info --format '{{.KernelVersion}}')
alpine=$(docker run --rm alpine:3.23 uname -r)
debian=$(docker run --rm debian:13-slim uname -r)
echo "engine: $engine"
echo "alpine: $alpine"
echo "debian: $debian"
[ "$engine" = "$alpine" ] && [ "$alpine" = "$debian" ] && echo "same kernel in every container"
```

```text
engine: 6.6.114.1-microsoft-standard-WSL2
alpine: 6.6.114.1-microsoft-standard-WSL2
debian: 6.6.114.1-microsoft-standard-WSL2
same kernel in every container
```

Two different Linux distributions, one kernel: the engine's. (On Docker Desktop the engine runs in a small Linux VM, so
you see that VM's kernel; on a Linux server you see the server's own kernel.) A VM would report its own guest kernel.

A container is just an isolated process. Inside, it sees only its own processes:

<!-- test: contains=PID; output -->
```bash
docker run --rm alpine:3.23 ps
```

```text
PID   USER     TIME  COMMAND
    1 root      0:00 ps
```

`ps` is process number 1: there is no boot process, no init system, no other services. That is why it starts so fast:

<!-- test: contains=real -->
```bash
time docker run --rm alpine:3.23 true
```

On a typical laptop this takes about half a second, and most of it is Docker setting up the container, not booting
anything. Compare the image sizes too:

<!-- test: contains=alpine:3.23 -->
```bash
docker image ls alpine:3.23
```

An Alpine image is under 10 MB; a minimal VM disk image is usually hundreds of megabytes or more.

## Command breakdown

| Command | What it does |
|---|---|
| `docker info --format '{{.KernelVersion}}'` | print one field of the engine's information (lesson 005) |
| `uname -r` | print the release of the running kernel |
| `ps` | list the processes this container can see |
| `time COMMAND` | measure how long a command takes (a shell feature) |

## Hands-on lab

**Instructions.** Start an Ubuntu container and a BusyBox container, and show that both report the engine's kernel even
though Ubuntu and BusyBox are completely different user spaces.

**Expected result.** Both print the same kernel release as `docker info --format '{{.KernelVersion}}'`.

**Verification.**

<!-- test: contains=match -->
```bash
[ "$(docker run --rm ubuntu:24.04 uname -r)" = "$(docker run --rm busybox:1.37 uname -r)" ] && echo "kernels match"
```

## Break it

Because the kernel is shared, a container must not be allowed to change kernel settings for everyone. Try it:

<!-- test: fail; contains=Read-only file system; output -->
```bash
docker run --rm alpine:3.23 sysctl -w net.ipv4.ip_forward=0
```

```text
sysctl: error setting key 'net.ipv4.ip_forward': Read-only file system
```

## Troubleshoot it

`Read-only file system`: Docker mounts `/proc/sys` (the kernel's settings) read-only inside the container. In a VM you
own the kernel and could change it; in a container you would be changing the kernel of the host and every other
container on it. This is a security boundary, not a bug. Look at how `/proc/sys` is mounted:

<!-- test: contains=ro -->
```bash
docker run --rm alpine:3.23 sh -c 'grep " /proc/sys " /proc/mounts'
```

## Fix it

Some kernel settings are **namespaced**: each container has its own copy (most network settings are). Docker lets you
set those at start time, safely, with `--sysctl`:

<!-- test: contains=net.ipv4.ip_forward = 1; output -->
```bash
docker run --rm --sysctl net.ipv4.ip_forward=1 alpine:3.23 sysctl net.ipv4.ip_forward
```

```text
net.ipv4.ip_forward = 1
```

Settings that are not namespaced (memory management, most of `kernel.*`) can only be changed on the host. If an
application truly needs its own kernel or kernel modules, it needs a VM, not a container.

## Practice challenge

A container only sees its own processes. Prove it: start a long-running container in the background, then list the
processes from a **second** container. Does the second one see the first one's `sleep`?

<details>
<summary>Solution</summary>

<!-- test: contains=sleep-absent; output -->
```bash
docker run -d --name sleeper alpine:3.23 sleep 300 > /dev/null
docker run --rm alpine:3.23 ps | grep -q sleep && echo "sleep-visible" || echo "sleep-absent"
docker rm -f sleeper > /dev/null
```

```text
sleep-absent
```

Each container has its own **PID namespace**: process 1 of every container is its own command, and it cannot see the
processes of other containers (the host can see all of them). `-d` runs in the background (lesson 009).

</details>

## Real-world example

A cloud provider runs customers' workloads in VMs, because different customers must never share a kernel. Inside each
customer's VM, the customer runs dozens of containers for their own services: fast to deploy, cheap to run, and isolated
enough between services of the same team. Kubernetes nodes are usually exactly that: VMs that run containers.

## Recap

- A VM virtualises hardware and runs a full guest OS with its own kernel.
- A container is an isolated process sharing the host's kernel: small, fast to start, weaker isolation.
- Kernel settings are protected inside containers; only namespaced ones can be set, with `--sysctl`.
- VMs and containers are complementary: containers usually run inside VMs in the cloud.

## Cleanup

Nothing to clean: `--rm` removed every container and the challenge removed `sleeper`.

Next: [Lesson 004 · Docker architecture](../004-docker-architecture/README.md)
