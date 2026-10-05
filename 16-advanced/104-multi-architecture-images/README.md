# Lesson 104 · Multi-architecture images

> Level 17 · Advanced Docker · ⏱ 30 minutes · run every command from the course folder

## What are we learning?

A container image contains machine code for one CPU architecture: an `amd64` (x86-64) binary does not run on an
`arm64` processor (Apple silicon, AWS Graviton, Raspberry Pi) without emulation. A **multi-architecture image** is one
name, one tag, with a variant per platform behind it (an **image index**, also called a manifest list). `docker pull`
and `docker run` pick the variant that matches the machine automatically. `docker buildx build --platform …` builds
all variants in one command.

## Visual

```text
  cafe-hello:1.0  (image index)
    ├── linux/amd64  → manifest → layers with x86-64 machine code     ◀── picked on a laptop / most servers
    └── linux/arm64  → manifest → layers with ARM64 machine code      ◀── picked on Apple silicon, Graviton

  How it is built (cross-compilation, fast):
  ┌─────────────────────────────── build machine (amd64) ───────────────────────────────┐
  │ FROM --platform=$BUILDPLATFORM golang   runs natively, once per target              │
  │   GOOS=$TARGETOS GOARCH=$TARGETARCH go build   → hello (amd64), hello (arm64)       │
  │ FROM scratch + COPY hello                    → one small image per platform         │
  └─────────────────────────────────────────────────────────────────────────────────────┘
  Alternative: build every stage under emulation (QEMU), slower but works for any language.
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-104 16-advanced/104-multi-architecture-images/examples
cd ~/docker-practice/lesson-104
cat Dockerfile
```

## Demonstration

Which platforms can this engine's builder produce?

<!-- test: contains=linux/arm64; output -->
```bash
docker buildx inspect --bootstrap | grep -i '^platforms'
```

```text
Platforms:        linux/amd64, linux/amd64/v2, linux/amd64/v3, linux/arm64, linux/riscv64, linux/ppc64le, linux/s390x, linux/arm/v7, linux/arm/v6
```

Build for two platforms. `--load` stores the result in the engine's image store (this needs the containerd image
store, the default for new Docker Desktop and Docker Engine 29 installations; see Troubleshoot it):

<!-- test: contains=cafe-hello:1.0 -->
```bash
docker buildx build -q --platform linux/amd64,linux/arm64 -t cafe-hello:1.0 --load . > /dev/null
docker image ls cafe-hello --format '{{.Repository}}:{{.Tag}}'
```

One tag, two variants:

<!-- test: contains=linux/amd64; contains=linux/arm64; output -->
```bash
docker image ls --tree cafe-hello
```

```text
IMAGE                ID             DISK USAGE   CONTENT SIZE   EXTRA
cafe-hello:1.0       ece6197c65c4        5.2MB         2.79MB        
├─ linux/amd64       68f2b68e502b       3.86MB         1.44MB        
└─ linux/arm64       42bc0ea73444       1.34MB         1.34MB        
```

Run each variant. The engine picks its own platform by default; `--platform` asks for another one, which Docker
Desktop runs through emulation (QEMU):

<!-- test: contains=hello from linux/amd64; contains=hello from linux/arm64; output -->
```bash
docker run --rm cafe-hello:1.0
docker run --rm --platform linux/arm64 cafe-hello:1.0
```

```text
hello from linux/amd64
hello from linux/arm64
```

## Command breakdown

| Command / instruction | What it does |
|---|---|
| `docker buildx build --platform linux/amd64,linux/arm64` | build one variant per platform |
| `--load` / `--push` | store the result in the local engine / push it to a registry (lesson 076) |
| `FROM --platform=$BUILDPLATFORM …` | run this stage on the build machine's own platform |
| `ARG TARGETOS TARGETARCH` | the platform being built, set by buildx for every variant |
| `docker image ls --tree NAME` | the platform variants of a local image |
| `docker run --platform linux/arm64` | run a specific variant (emulated if it is not the machine's) |
| `docker buildx imagetools inspect REF` | the variants of an image in a registry |

## Hands-on lab

**Instructions.** Build only an `arm64` variant under the tag `cafe-hello:arm`, and show its architecture with
`docker image inspect`.

**Expected result.** `linux/arm64`.

**Verification.**

<!-- test: contains=linux/arm64 -->
```bash
docker buildx build -q --platform linux/arm64 -t cafe-hello:arm --load . > /dev/null
docker image inspect --format '{{.Os}}/{{.Architecture}}' cafe-hello:arm
```

## Break it

A colleague needs the image on a Raspberry Pi with a 32-bit operating system (`linux/arm/v7`):

<!-- test: fail; anyof=does not provide the specified platform||no matching manifest||pull access denied||docker.io/library/cafe-hello:1.0; output -->
```bash
docker run --rm --platform linux/arm/v7 cafe-hello:1.0 2>&1
```

```text
Unable to find image 'cafe-hello:1.0' locally
docker: Error response from daemon: pull access denied for cafe-hello, repository does not exist or may require 'docker login'

Run 'docker run --help' for more information
```

## Troubleshoot it

The image index has no `arm/v7` variant. Docker found the tag locally, but nothing for that platform, so it tried to
pull it from Docker Hub, where `cafe-hello` does not exist (`pull access denied`; an engine that pulls through a
registry mirror reports the failed lookup of `docker.io/library/cafe-hello:1.0` in the mirror's own words). List what the tag contains:

<!-- test: absent=arm/v7; output -->
```bash
docker image ls --tree cafe-hello
```

```text
IMAGE                ID             DISK USAGE   CONTENT SIZE   EXTRA
cafe-hello:1.0       ece6197c65c4       7.54MB         2.79MB        
├─ linux/amd64       68f2b68e502b       3.86MB         1.44MB        
└─ linux/arm64       42bc0ea73444       3.68MB         1.34MB        

cafe-hello:arm       dca66b67445a       3.68MB         1.34MB        
└─ linux/arm64       42bc0ea73444       3.68MB         1.34MB        
```

Other errors of this family and their causes:

| Message | Cause |
|---|---|
| `exec format error` | a binary for another architecture without emulation (QEMU/binfmt not installed on that Linux host) |
| `docker exporter does not currently support exporting manifest lists` | `--load` of several platforms on the classic image store: push to a registry instead, or enable the containerd image store |
| `no match for platform in manifest` | pulling an image that was published for other platforms only |

## Fix it

Add the platform to the build. Go cross-compiles for it, and `scratch` needs no base image, so nothing new is
downloaded:

<!-- test: contains=linux/arm/v7; output -->
```bash
docker buildx build -q --platform linux/amd64,linux/arm64,linux/arm/v7 -t cafe-hello:1.0 --load . > /dev/null
docker image ls --tree cafe-hello
```

```text
IMAGE                 ID             DISK USAGE   CONTENT SIZE   EXTRA
cafe-hello:1.0        6edd47fa2b03       8.88MB         4.12MB        
├─ linux/amd64        68f2b68e502b       3.86MB         1.44MB        
├─ linux/arm64        42bc0ea73444       3.68MB         1.34MB        
└─ linux/arm/v7       5b50b1c416e0       1.33MB         1.33MB        

cafe-hello:arm        dca66b67445a       3.68MB         1.34MB        
└─ linux/arm64        42bc0ea73444       3.68MB         1.34MB        
```

The Raspberry Pi now pulls the `arm/v7` variant and runs it natively. Running that variant **here** needs emulation for
32-bit ARM, which not every Docker installation has; without it you get `exec format error`, the first message of the
table above.

## Practice challenge

Prove that the build stage ran on the build machine's own platform and was **not** emulated: add a temporary `RUN`
step that prints `$BUILDPLATFORM`, `$TARGETPLATFORM` and `uname -m` in the build stage, and build for `linux/arm64`
with plain progress output.

<details>
<summary>Solution</summary>

<!-- test: contains=TARGETPLATFORM=linux/arm64; contains=uname=x86_64; output -->
```bash
awk '/^RUN CGO_ENABLED/ {
  print "ARG BUILDPLATFORM TARGETPLATFORM"
  print "RUN echo \"BUILDPLATFORM=$BUILDPLATFORM TARGETPLATFORM=$TARGETPLATFORM uname=$(uname -m)\""
} { print }' Dockerfile > Dockerfile.debug
docker buildx build --no-cache --progress plain --platform linux/arm64 -f Dockerfile.debug -t cafe-hello:debug . 2>&1 |
  grep -o 'BUILDPLATFORM=.*uname=[a-z0-9_]*$' | head -1
```

```text
BUILDPLATFORM=linux/amd64 TARGETPLATFORM=linux/arm64 uname=x86_64
```

The build stage reports the machine's own architecture (`x86_64` here; `aarch64` on an ARM machine) while building for
`linux/arm64`: the Go compiler did the cross-compilation, natively and quickly.

</details>

## Real-world example

A company moves part of its services to ARM-based cloud instances, which cost less for the same work. Its CI builds
every image with `--platform linux/amd64,linux/arm64 --push`, so the same tag runs on both the old and new node pools;
Kubernetes nodes simply pull the variant for their CPU. For Go and Rust services, cross-compilation keeps the build
time close to a single-platform build; for languages without easy cross-compilation, the CI uses ARM build machines or
QEMU emulation.

## Recap

- An image index groups one variant per platform under one tag; the engine picks the matching one.
- `docker buildx build --platform a,b` builds all variants; `--push` (or `--load` with the containerd image store).
- `FROM --platform=$BUILDPLATFORM` + `TARGETOS/TARGETARCH` cross-compiles natively instead of emulating.
- "does not provide the specified platform": the variant does not exist; "exec format error": no emulation.

## Cleanup

<!-- test -->
```bash
docker image rm -f cafe-hello:1.0 cafe-hello:arm cafe-hello:debug > /dev/null 2>&1 || true
docker buildx prune -f > /dev/null
cd ~ && rm -rf ~/docker-practice/lesson-104
```

Next: [Lesson 105 · Build cache optimization](../105-cache-optimization/README.md)
