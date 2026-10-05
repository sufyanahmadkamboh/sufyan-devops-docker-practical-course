# Lesson 007 · Images vs containers

> Level 2 · First container · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

An **image** is a read-only template: a file system plus metadata (which command to run, which user, which ports). A
**container** is an instance of an image: the image's layers, plus a thin **writable layer** of its own, plus a running
(or stopped) process. One image can be the template for any number of containers, and changes inside a container never
change the image. The analogy: an image is a class, a container is an object.

## Visual

```text
                          Image  alpine:3.23   (read-only, shared)
                     ┌──────────────────────────────────────────────┐
                     │ layer: Alpine file system  /bin /etc /lib …  │
                     └──────────────────────────────────────────────┘
                          ▲                ▲                 ▲
          ┌───────────────┴──┐   ┌─────────┴────────┐   ┌────┴─────────────┐
          │ writable layer   │   │ writable layer   │   │ writable layer   │
          │  /data.txt = red │   │  /data.txt = blue│   │  (no changes)    │
          │ container "red"  │   │ container "blue" │   │ container "plain"│
          └──────────────────┘   └──────────────────┘   └──────────────────┘
       Each container sees the image + its own changes. The image never changes.
```

| | Image | Container |
|---|---|---|
| What it is | template: files + metadata | instance: image + writable layer + process |
| Changes? | never (read-only) | yes, in its writable layer |
| Lifetime | until you remove it | created → running → exited → removed |
| Listed by | `docker image ls` | `docker ps -a` |

## Lab setup

No files are needed.

## Demonstration

Create three containers from the same image. Two of them write a different file:

<!-- test: contains=blue; output -->
```bash
docker run --name red alpine:3.23 sh -c 'echo red > /data.txt'
docker run --name blue alpine:3.23 sh -c 'echo blue > /data.txt'
docker run --name plain alpine:3.23 true
docker ps -a --filter ancestor=alpine:3.23 --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
```

```text
NAMES     IMAGE         STATUS
plain     alpine:3.23   Exited (0) Less than a second ago
blue      alpine:3.23   Exited (0) 1 second ago
red       alpine:3.23   Exited (0) 2 seconds ago
```

Three containers, one image. `docker container diff` shows what each container changed compared with its image
(`A` added, `C` changed, `D` deleted):

<!-- test: contains=A /data.txt; output -->
```bash
echo "red:";   docker container diff red
echo "blue:";  docker container diff blue
echo "plain:"; docker container diff plain
```

```text
red:
A /data.txt
blue:
A /data.txt
plain:
```

`plain` changed nothing. The files written by `red` and `blue` live only in their own writable layers. A **new**
container from the same image does not see them:

<!-- test: contains=No such file; output -->
```bash
docker run --rm alpine:3.23 cat /data.txt 2>&1 || true
```

```text
cat: can't open '/data.txt': No such file or directory
```

A stopped container still has its writable layer. `docker cp` can copy a file out of it, even though nothing is running:

<!-- test: contains=red; output -->
```bash
docker cp red:/data.txt ./red-data.txt
cat red-data.txt
rm red-data.txt
```

```text
red
```

## Command breakdown

| Command | What it does |
|---|---|
| `docker run --name NAME IMAGE CMD` | create and start a named container (lesson 010) |
| `docker container diff NAME` | files the container added (A), changed (C) or deleted (D) |
| `docker cp NAME:PATH DEST` | copy a file out of a container (running or stopped) |
| `docker image ls` | the images on this machine |
| `docker ps -a --filter ancestor=IMAGE` | the containers created from IMAGE |

## Hands-on lab

**Instructions.** Start a container named `deleter` from `alpine:3.23` that deletes `/etc/motd`. Then show, with
`docker container diff`, what changed, and prove that a fresh container from the same image still has `/etc/motd`.

**Expected result.** `D /etc/motd` in the diff, and the fresh container lists `/etc/motd`.

**Verification.**

<!-- test: contains=D /etc/motd; contains=/etc/motd -->
```bash
docker run --name deleter alpine:3.23 rm /etc/motd
docker container diff deleter
docker run --rm alpine:3.23 ls /etc/motd
```

## Break it

Turn the `red` container into an image of its own with `docker commit` (it saves a container's writable layer as a new
image; lesson 022 shows the right way to build images), start a container from it, and then try to delete the image:

<!-- test: fail; contains=is using its referenced image; output -->
```bash
docker commit red lesson-007:red > /dev/null
docker create --name from-red lesson-007:red cat /data.txt > /dev/null
docker image rm lesson-007:red
```

```text
Error response from daemon: conflict: unable to delete lesson-007:red (must be forced) - container df32e98cefb6 is using its referenced image 40b46fbef5bd
```

## Troubleshoot it

`conflict: unable to delete … container … is using its referenced image`: a container is built **on top of** its
image's layers. Even a stopped container needs them, so Docker refuses to delete an image while any container, running
or not, was created from it. Find the containers that use it:

<!-- test: contains=from-red; output -->
```bash
docker ps -a --filter ancestor=lesson-007:red --format '{{.Names}}: {{.Status}}'
```

```text
from-red: Created
```

## Fix it

Remove the containers first, then the image:

<!-- test: contains=Deleted -->
```bash
docker rm from-red > /dev/null
docker image rm lesson-007:red
```

`docker image rm -f` would remove the tag anyway, but it leaves the containers pointing at an image without a name.
Remove the containers first.

## Practice challenge

Prove that one image can run several containers **at the same time**: start three `alpine:3.23` containers in the
background running `sleep 300`, show that all three are running from the same image ID, then remove them.

<details>
<summary>Solution</summary>

<!-- test: contains=3 running; output -->
```bash
for n in one two three; do docker run -d --name "sleep-$n" alpine:3.23 sleep 300 > /dev/null; done
docker ps --filter name=sleep- --format '{{.Names}} {{.Image}}'
echo "$(docker ps -q --filter ancestor=alpine:3.23 | wc -l | tr -d ' ') running"
docker inspect --format '{{.Image}}' sleep-one sleep-two sleep-three | sort -u | wc -l | tr -d ' '
docker rm -f sleep-one sleep-two sleep-three > /dev/null
```

```text
sleep-three alpine:3.23
sleep-two alpine:3.23
sleep-one alpine:3.23
3 running
1
```

The last number is `1`: one image ID behind three containers. `-d` starts a container in the background (lesson 009).

</details>

## Real-world example

A web shop runs 12 replicas of its API in production: 12 containers from one image `shop-api:2.4.1`. A fix is never
applied inside a running container (that change would be lost, and the 12 containers would drift apart). The team
builds `shop-api:2.4.2` and replaces the containers. `docker commit` exists, but images built from a Dockerfile are
reproducible and reviewable, which is why teams use those instead.

## Recap

- Image: read-only template. Container: image + its own writable layer + a process.
- Many containers can run from one image; their changes stay in their own writable layers.
- `docker container diff` shows a container's changes; `docker cp` copies files out.
- An image cannot be removed while containers created from it exist: remove the containers first.

## Cleanup

<!-- test -->
```bash
docker rm -f red blue plain deleter > /dev/null
docker image rm -f lesson-007:red > /dev/null 2>&1 || true
```

Next: [Lesson 008 · Listing containers](../008-listing-containers/README.md)
