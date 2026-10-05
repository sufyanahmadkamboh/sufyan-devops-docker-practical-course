# Lesson 023 · FROM: choosing a base image

> Level 5 · Dockerfiles · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

Every Dockerfile starts with `FROM`: the **base image** whose files become the bottom layers of your image. The choice
decides the image's size, which tools exist (a shell? `bash`? a package manager?), the C library (`glibc` or `musl`),
and how many packages, and therefore vulnerabilities, you ship. Choose deliberately and always with an explicit tag.

## Visual

```text
  Base image families (each with a tag, never just the name)

  ubuntu:24.04 / debian:13-slim   full or slim Linux distribution · glibc · apt · bash        tens of MB to ~100 MB
  alpine:3.23                     minimal distribution · musl · apk · busybox sh (no bash)    under 10 MB
  python:3.14-slim, node:24-alpine  a language runtime on top of one of the above             what most apps use
  gcr.io/distroless/…             only the runtime and its libraries: no shell, no package manager
  scratch                         empty: for a single static binary (lesson 089)

  smaller base ─▶ fewer packages ─▶ smaller attack surface, faster pulls ─▶ but fewer tools for you
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-023
cd ~/docker-practice/lesson-023
```

## Demonstration

Compare the sizes of the bases you have:

<!-- test: contains=alpine:3.23; contains=debian:13-slim -->
```bash
for image in busybox:1.37 alpine:3.23 debian:13-slim ubuntu:24.04 gcr.io/distroless/static-debian12:nonroot; do
  docker image ls --format '{{.Size}}\t{{.Repository}}:{{.Tag}}' "$image"
done
```

The language images show the cost of a full distribution: compare the two Python variants.

<!-- test: contains=python:3.14-alpine; contains=python:3.14-slim; output -->
```bash
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.Size}}' python
```

```text
python:3.14-slim  192MB
python:3.14-alpine  82.6MB
```

What each base contains matters as much as its size. Look for common tools in three distributions:

<!-- test: contains=alpine:3.23; output -->
```bash
for image in alpine:3.23 debian:13-slim ubuntu:24.04; do
  tools=$(docker run --rm "$image" sh -c 'for t in sh bash apk apt-get curl; do command -v $t > /dev/null && printf "%s " $t; done; true')
  echo "$image: $tools"
done
```

```text
alpine:3.23: sh apk 
debian:13-slim: sh bash apt-get 
ubuntu:24.04: sh bash apt-get 
```

None of them has `curl`: base images are deliberately minimal, and you install what your application needs (lesson
026). Alpine has no `bash` and uses `apk`; Debian and Ubuntu use `apt-get`.

## Command breakdown

| Instruction | Meaning |
|---|---|
| `FROM IMAGE:TAG` | start from this image; always with a tag (lesson 021) |
| `FROM IMAGE@sha256:…` | start from an exact image by digest (lesson 018) |
| `FROM IMAGE AS NAME` | name the stage, for multi-stage builds (lesson 087) |
| `FROM scratch` | start from an empty file system |
| `ARG V=…` + `FROM image:${V}` | choose the tag with a build argument (lesson 031) |

## Hands-on lab

**Instructions.** Write a Dockerfile `FROM debian:13-slim` whose container prints the `PRETTY_NAME` line of
`/etc/os-release`, build it as `base-demo:debian`, and run it.

**Expected result.** `PRETTY_NAME="Debian GNU/Linux 13 (trixie)"`.

**Verification.**

<!-- test: contains=Debian GNU/Linux 13 -->
```bash
cd ~/docker-practice/lesson-023
printf 'FROM debian:13-slim\nCMD ["grep", "PRETTY_NAME", "/etc/os-release"]\n' > Dockerfile.debian
docker build -q -f Dockerfile.debian -t base-demo:debian . > /dev/null
docker run --rm base-demo:debian
```

## Break it

A build step copied from a Debian-based Dockerfile, now on Alpine:

<!-- test: contains=bash: not found; output -->
```bash
printf 'FROM alpine:3.23\nRUN bash -c "echo preparing the image"\n' > Dockerfile.alpine
docker build --progress=plain -f Dockerfile.alpine -t base-demo:alpine . 2>&1 | grep -E 'not found|ERROR'
```

```text
#5 0.175 /bin/sh: bash: not found
#5 ERROR: process "/bin/sh -c bash -c \"echo preparing the image\"" did not complete successfully: exit code: 127
0.175 /bin/sh: bash: not found
ERROR: failed to build: failed to solve: process "/bin/sh -c bash -c \"echo preparing the image\"" did not complete successfully: exit code: 127
```

## Troubleshoot it

Exit code **127** always means "command not found", and the step's output names it: `bash: not found`. The base image
does not contain the program. Check what the image provides:

<!-- test: contains=no bash; output -->
```bash
docker run --rm alpine:3.23 sh -c 'command -v bash || echo "no bash"; ls -l /bin/sh'
```

```text
no bash
lrwxrwxrwx    1 root     root            12 Sep 17 17:32 /bin/sh -> /bin/busybox
```

Alpine's shell is BusyBox `sh`. The same happens with `apt-get` on Alpine, `apk` on Debian, or any shell at all in
distroless images.

## Fix it

Either write the step for the base you chose (POSIX `sh` is enough here), or install the missing tool with the base's
package manager (`RUN apk add --no-cache bash`), or choose a base that has it. The simplest fix:

<!-- test: contains=preparing the image -->
```bash
printf 'FROM alpine:3.23\nRUN sh -c "echo preparing the image"\n' > Dockerfile.alpine
docker build --progress=plain -f Dockerfile.alpine -t base-demo:alpine . 2>&1 | grep "preparing the image"
```

## Practice challenge

Alpine uses the `musl` C library, Debian `glibc`; a program compiled for one may not run on the other. Find the dynamic
loader of each base under `/lib` to see which C library it uses.

<details>
<summary>Solution</summary>

<!-- test: contains=ld-musl; contains=ld-linux; output -->
```bash
docker run --rm alpine:3.23 sh -c 'ls /lib | grep "^ld-"'
docker run --rm debian:13-slim sh -c 'ls /lib64 /lib/x86_64-linux-gnu 2>/dev/null | grep "^ld-" | head -1'
```

```text
ld-musl-x86_64.so.1
ld-linux-x86-64.so.2
```

`ld-musl…` is musl, `ld-linux…` is glibc. Pre-compiled binaries (some Python wheels, Node.js native modules,
vendor tools) are often built for glibc only: on Alpine they fail with confusing "not found" errors, although the file
exists. That is a common reason to choose a `-slim` (Debian) base instead of `-alpine`. (On an ARM computer the names
end in `aarch64`.)

</details>

## Real-world example

A team standardises on `python:3.14-slim` for its APIs: Debian's glibc runs every pre-built wheel, and the slim variant
leaves out compilers and documentation. Static Go services use `gcr.io/distroless/static` or `scratch` (a few MB, no
shell to exploit), and the base tags are pinned and updated by a bot that opens a pull request for each new patch
release, so base updates are reviewed and tested like code changes.

## Recap

- `FROM` chooses the base image: size, tools, C library and vulnerabilities come with it.
- Alpine: tiny, `musl`, `apk`, BusyBox `sh`; Debian/Ubuntu: `glibc`, `apt-get`, `bash`; distroless: no shell.
- Exit code 127 / `not found`: the base image does not contain that program.
- Always pin the tag (or digest); never rely on `latest`.

## Cleanup

<!-- test -->
```bash
docker image rm -f base-demo:debian base-demo:alpine > /dev/null
rm -rf ~/docker-practice/lesson-023
```

Next: [Lesson 024 · WORKDIR](../024-workdir/README.md)
