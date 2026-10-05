# Lesson 103 · BuildKit and buildx

> Level 17 · Advanced Docker · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

Since Docker 23, every `docker build` runs on **BuildKit**, the build engine, through the **buildx** client plugin
(`docker build` is an alias of `docker buildx build`). BuildKit is what makes the features of the last lessons possible:
parallel stages, cache mounts and secret mounts (`RUN --mount`), multi-platform builds (lesson 104), and **outputs**
other than an image: files on your disk, a tar archive, an OCI layout, or a push straight to a registry. buildx also
manages **builders**: the engine's own, or separate BuildKit instances in a container, on another machine, or in
Kubernetes.

## Visual

```text
  docker build / docker buildx build
          │ (Dockerfile + build context)
          ▼
  ┌───────────────────── builder (BuildKit) ─────────────────────┐
  │ stages run in parallel when they do not depend on each other │
  │ cache · RUN --mount=type=cache|secret|ssh · --platform …     │
  └───────┬──────────────┬───────────────┬───────────────┬───────┘
          ▼              ▼               ▼               ▼
     --load          --output         --output        --push
     image in the    type=local       type=tar        image in a
     local engine    dest=out/        dest=fs.tar     registry
                     (files on disk)
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-103 examples/go-api
cp 16-advanced/103-buildx/examples/Dockerfile ~/docker-practice/lesson-103/
cd ~/docker-practice/lesson-103
grep -n "^FROM" Dockerfile
```

A three-stage Dockerfile for the Go API: `build` compiles, `export` contains only the binary, `image` is the runnable
image.

## Demonstration

The buildx version and the builders this client knows (`*` marks the one in use; the `docker` driver is the engine's
built-in BuildKit):

<!-- test: contains=buildx; contains=docker; output -->
```bash
docker buildx version | cut -d' ' -f1,2
docker buildx ls --format '{{.Name}} {{.DriverEndpoint}}' 2>/dev/null || docker buildx ls
```

```text
github.com/docker/buildx v0.33.0-desktop.1
default docker
default default
```

A normal build of the default (last) stage, with the full plain progress log:

<!-- test: contains=cafe-go:1.0 -->
```bash
docker buildx build --progress plain -t cafe-go:1.0 --load . 2>&1 | grep -E '^#[0-9]+ \[' | head -8
docker image ls cafe-go --format '{{.Repository}}:{{.Tag}}'
```

Instead of an image, ask BuildKit for **files**: the `export` stage written to a folder on your disk. No image is
created; you get the compiled program:

<!-- test: contains=E   L   F; output -->
```bash
docker buildx build -q --target export --output type=local,dest=out . > /dev/null
ls out
head -c 4 out/go-api | od -c | head -1
```

```text
go-api
0000000 177   E   L   F
```

`177 E L F` are the first bytes of a Linux executable. CI pipelines use this to build release binaries in a clean,
pinned toolchain without installing Go on the CI machine.

## Command breakdown

| Command / option | What it does |
|---|---|
| `docker buildx ls` | the builders and their platforms |
| `docker buildx build --progress plain` | full log of every step (`auto`, `tty`, `quiet` also exist) |
| `--target STAGE` | build up to that stage only |
| `--output type=local,dest=DIR` | write the result's files into DIR |
| `--output type=tar,dest=FILE.tar` | the same, as one tar file |
| `--load` / `--push` | the result as an image in the engine / in a registry |
| `docker buildx du` | disk used by the build cache |
| `docker buildx prune` | remove build cache |
| `docker buildx create --driver docker-container` | a separate BuildKit instance (pulls the `moby/buildkit` image) |

## Hands-on lab

**Instructions.** Show how much disk the build cache uses now, then build only the `build` stage with
`--target build` and load it as `cafe-go:build-stage`. Compare its size with `cafe-go:1.0`.

**Expected result.** The build stage (Go toolchain included) is many times larger than the final image.

**Verification.**

<!-- test: contains=cafe-go:build-stage; contains=cafe-go:1.0 -->
```bash
docker buildx du | tail -1
docker buildx build -q --target build -t cafe-go:build-stage --load . > /dev/null
for image in cafe-go:build-stage cafe-go:1.0; do
  echo "$image $(docker image inspect --format '{{.Size}}' "$image" | awk '{printf "%.1f MB", $1/1000000}')"
done
```

## Break it

A script builds the build stage with a typo:

<!-- test: fail; contains=biuld; output -->
```bash
docker buildx build --target biuld -t cafe-go:build-stage . 2>&1 | grep ERROR
test "${PIPESTATUS[0]}" -eq 0
```

```text
ERROR: failed to build: failed to solve: target stage "biuld" could not be found (did you mean build?)
```

## Troubleshoot it

BuildKit reads the whole Dockerfile before it builds anything, and refuses a target that is not one of the stage
names given with `AS`. List them:

<!-- test: contains=AS build; output -->
```bash
grep -n ' AS ' Dockerfile
```

```text
2:FROM golang:1.26-alpine AS build
8:FROM scratch AS export
12:FROM gcr.io/distroless/static-debian12:nonroot AS image
```

## Fix it

<!-- test: contains=cafe-go:build-stage -->
```bash
docker buildx build -q --target build -t cafe-go:build-stage --load . > /dev/null
docker image ls cafe-go --format '{{.Repository}}:{{.Tag}}'
```

## Practice challenge

Export the complete file system of the final `image` stage as a tar file with `--output type=tar`, and list the files
it contains. How many files does the runnable image have?

<details>
<summary>Solution</summary>

<!-- test: contains=go-api; output -->
```bash
docker buildx build -q --output type=tar,dest=image.tar . > /dev/null
tar -tf image.tar | grep -v '/$' | wc -l
tar -tf image.tar | grep -E 'go-api|passwd'
```

```text
1335
etc/passwd
go-api
```

The final image is the distroless base (CA certificates, time zone data, `/etc/passwd` with a `nonroot` user, but no
shell, no package manager and no other programs) plus one binary: very little for an attacker to use (lesson 080).

</details>

## Real-world example

CI systems often run BuildKit as a separate service: GitHub Actions' `docker/setup-buildx-action` creates a
`docker-container` builder, `docker/build-push-action` builds with `--cache-from`/`--cache-to type=gha` (the cache is
stored in GitHub's cache service) and `--push`es multi-platform images in one step. Release pipelines of command-line
tools use `--output type=local` to produce binaries for every platform from one Dockerfile.

## Recap

- `docker build` runs on BuildKit through buildx; builders can be local, containerised or remote.
- `--target` builds one stage; `--output type=local|tar` writes files instead of an image.
- `--progress plain` shows every step; `docker buildx du` and `prune` manage the build cache.
- Wrong stage names fail before any step runs: stage names come from `FROM … AS name`.

## Cleanup

<!-- test -->
```bash
docker image rm -f cafe-go:1.0 cafe-go:build-stage > /dev/null 2>&1 || true
cd ~ && rm -rf ~/docker-practice/lesson-103
```

Next: [Lesson 104 · Multi-architecture images](../104-multi-architecture-images/README.md)
