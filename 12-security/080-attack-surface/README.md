# Lesson 080 · The attack surface of a container

> Level 13 · Container security · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

The **attack surface** is everything an attacker could use once they get code running in your container: a shell,
a package manager, network tools, setuid programs, the root user, Linux capabilities, a writable file system, access to
host devices. Each lesson of this module removes one part of it. This lesson shows you how to **see** the attack
surface, and the most dangerous single flag: `--privileged`.

## Visual

```text
  What an attacker finds inside the container           How this module shrinks it

  shell, package manager, curl, perl ......... (082)    minimal or distroless base image
  the root user ............................. (081)    USER appuser
  secrets in ENV, ARG, image layers ......... (083)    build secrets, runtime secrets
  writable file system ...................... (084)    --read-only + --tmpfs
  Linux capabilities (chown, kill, …) ....... (085)    --cap-drop ALL, add back only what is needed
  unlimited CPU, memory, processes .......... (086)    --memory, --cpus, --pids-limit
  host devices, all capabilities ............ (080)    never --privileged

        ┌──────────────── host kernel (shared by every container) ────────────────┐
        │   each item above is a step from "code runs in the container"          │
        │   towards "code controls the host"                                     │
        └─────────────────────────────────────────────────────────────────────────┘
```

## Lab setup

No files are needed: this lesson inspects images that are already on your computer.

## Demonstration

How many programs ship in a general-purpose base image, compared with a small one?

<!-- test: contains=alpine; output -->
```bash
echo "ubuntu:24.04  $(docker run --rm ubuntu:24.04 sh -c 'ls /bin /sbin /usr/bin /usr/sbin | wc -l') programs"
echo "alpine:3.23   $(docker run --rm alpine:3.23 sh -c 'ls /bin /sbin /usr/bin /usr/sbin | wc -l') programs"
```

```text
ubuntu:24.04  833 programs
alpine:3.23   320 programs
```

Every program is something an attacker can use. Some are more useful than others: a package manager installs more
tools, and **setuid** programs run with their owner's rights (usually root) whoever starts them:

<!-- test: contains=/usr/bin/passwd; output -->
```bash
docker run --rm ubuntu:24.04 find / -xdev -perm -4000 -type f
```

```text
/usr/bin/su
/usr/bin/chfn
/usr/bin/chsh
/usr/bin/passwd
/usr/bin/umount
/usr/bin/newgrp
/usr/bin/mount
/usr/bin/gpasswd
```

A **distroless** image goes further: no shell, no package manager, only the application and its runtime files. There is
nothing to run a shell with:

<!-- test: fail; anyof=executable file not found||no such file or directory; output -->
```bash
docker run --rm gcr.io/distroless/static-debian12:nonroot sh -c 'echo hello' 2>&1
```

```text
docker: Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: error during container init: exec: "sh": executable file not found in $PATH

Run 'docker run --help' for more information
```

## Command breakdown

| Command | What it shows |
|---|---|
| `ls /bin /sbin /usr/bin /usr/sbin \| wc -l` | how many programs are installed |
| `find / -xdev -perm -4000 -type f` | setuid programs (they run with the rights of their owner) |
| `gcr.io/distroless/static-debian12:nonroot` | an image with no shell or package manager, running as a non-root user |
| `--privileged` | gives the container every capability and every host device: almost the host itself |

## Hands-on lab

**Instructions.** Count the installed packages of `debian:13-slim` (`dpkg-query -f '.\n' -W | wc -l`) and of
`alpine:3.23` (`apk info | wc -l`). Which image has the smaller attack surface?

**Expected result.** Two numbers; Alpine has fewer packages.

**Verification.**

<!-- test: contains=packages -->
```bash
echo "debian:13-slim $(docker run --rm debian:13-slim sh -c "dpkg-query -f '.\n' -W | wc -l") packages"
echo "alpine:3.23    $(docker run --rm alpine:3.23 sh -c 'apk info | wc -l') packages"
```

## Break it

A teammate cannot get a tool to work in a container and "fixes" it with `--privileged`. Compare what a normal and a
privileged container can see and do:

<!-- test: contains=privileged; output -->
```bash
echo "normal:     $(docker run --rm alpine:3.23 sh -c 'ls /dev | wc -l') devices, $(docker run --rm alpine:3.23 grep CapEff /proc/self/status)"
echo "privileged: $(docker run --rm --privileged alpine:3.23 sh -c 'ls /dev | wc -l') devices, $(docker run --rm --privileged alpine:3.23 grep CapEff /proc/self/status)"
```

```text
normal:     15 devices, CapEff:	00000000a80425fb
privileged: 174 devices, CapEff:	000001ffffffffff
```

## Troubleshoot it

The privileged container sees every device of the host (disks included) and has **every** capability (`CapEff` with
all bits set): with the host's disk device, it can mount the host's file system and change anything on it. The kernel
settings are writable too:

<!-- test: contains=net.ipv4.ip_forward; output -->
```bash
docker run --rm --privileged alpine:3.23 sysctl -w net.ipv4.ip_forward=1
```

```text
net.ipv4.ip_forward = 1
```

In lesson 003 the same command failed with `Read-only file system`. To find privileged containers on a host, ask
Docker:

<!-- test: contains=Privileged=true -->
```bash
docker run -d --name too-powerful --privileged alpine:3.23 sleep 300 > /dev/null
docker ps -q | xargs docker inspect --format '{{.Name}} Privileged={{.HostConfig.Privileged}}'
```

## Fix it

Remove `--privileged`. Find out which permission the tool actually needs and grant only that (a single capability with
`--cap-add`, lesson 085, or a single device with `--device`):

<!-- test: contains=Privileged=false -->
```bash
docker rm -f too-powerful > /dev/null
docker run -d --name just-enough alpine:3.23 sleep 300 > /dev/null
docker inspect --format '{{.Name}} Privileged={{.HostConfig.Privileged}}' just-enough
docker rm -f just-enough > /dev/null
```

## Practice challenge

Find out whether `ubuntu:24.04`, `alpine:3.23` and the distroless image contain a shell, a package manager and `wget`
or `curl`. Use `docker run --rm --entrypoint …` or `ls` in images that have a shell; for the distroless image, explain
why you cannot look inside it the same way.

<details>
<summary>Solution</summary>

<!-- test: contains=alpine:3.23; output -->
```bash
for image in ubuntu:24.04 alpine:3.23; do
  echo "$image: $(docker run --rm "$image" sh -c 'for t in sh bash apt-get apk wget curl; do command -v $t > /dev/null && printf "%s " $t; done')"
done
```

```text
ubuntu:24.04: sh bash apt-get 
alpine:3.23: sh apk wget 
```

The distroless image has no shell, so there is nothing to run `command -v` with: that is the point. You inspect it from
the outside instead, for example by listing its files with `docker export` (lesson 082) or its layers with
`docker history`.

</details>

## Real-world example

Security reviews of container platforms start with the questions of this module: which base image, which user, which
capabilities, is the file system read-only, are there limits, is anything privileged? Kubernetes enforces the answers
with **Pod Security Standards**: the `restricted` profile rejects privileged containers, root users and extra
capabilities before they ever start.

## Recap

- The attack surface is every tool, permission and resource available inside the container.
- Fewer programs, no setuid binaries, no shell (distroless) = less for an attacker to use.
- `--privileged` gives the container all capabilities and all host devices: never use it to "make something work".
- Find privileged containers with `docker inspect --format '{{.HostConfig.Privileged}}'`.

## Cleanup

<!-- test -->
```bash
docker rm -f too-powerful just-enough > /dev/null 2>&1 || true
```

Next: [Lesson 081 · Running as a non-root user](../081-non-root-users/README.md)
