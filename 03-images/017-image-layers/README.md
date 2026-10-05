# Lesson 017 · Image layers

> Level 4 · Images · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

An image is not one big file. It is a stack of read-only **layers**: each step that changes files when the image is
built (a `RUN`, `COPY` or `ADD` in a Dockerfile) adds one layer on top of the previous ones. A container adds one thin
**writable layer** on top. Layers are stored once and shared between images and containers, and they explain why an
image is as big as it is.

## Visual

```text
  docker image history nginx:1.30-alpine          (newest layer on top)

  ┌──────────────────────────────────────────┐
  │ container's writable layer (per container)│  ← changes made while it runs; removed with the container
  ╞══════════════════════════════════════════╡
  │ RUN … install nginx modules      51.9 MB │  ┐
  │ COPY docker-entrypoint scripts    ~60 kB │  │ read-only image layers,
  │ RUN … install nginx               5.6 MB │  │ shared by every container of the image
  │ ADD alpine-minirootfs …           9.1 MB │  ┘ ← the base image
  └──────────────────────────────────────────┘
  ENV, CMD, EXPOSE, LABEL … only change metadata: 0 B, no new file layer
```

A file deleted in a later layer is only hidden: its bytes stay in the layer that created it.

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-017 03-images/017-image-layers/examples
cd ~/docker-practice/lesson-017
ls
```

Two Dockerfiles: `broken/` creates and deletes a 20 MB file in two steps, `fixed/` in one.

## Demonstration

Every step of the build of the official `nginx:1.30-alpine` image is recorded:

<!-- test: contains=CREATED BY; output -->
```bash
docker image history nginx:1.30-alpine
```

```text
IMAGE          CREATED       CREATED BY                                      SIZE      COMMENT
0985e772fb9f   12 days ago   RUN /bin/sh -c set -x     && apkArch="$(cat …   51.9MB    buildkit.dockerfile.v0
<missing>      12 days ago   ENV ACME_VERSION=0.4.1                          0B        buildkit.dockerfile.v0
<missing>      12 days ago   ENV NJS_RELEASE=1                               0B        buildkit.dockerfile.v0
<missing>      12 days ago   ENV NJS_VERSION=1.0.1                           0B        buildkit.dockerfile.v0
<missing>      12 days ago   CMD ["nginx" "-g" "daemon off;"]                0B        buildkit.dockerfile.v0
<missing>      12 days ago   STOPSIGNAL SIGQUIT                              0B        buildkit.dockerfile.v0
<missing>      12 days ago   EXPOSE map[80/tcp:{}]                           0B        buildkit.dockerfile.v0
<missing>      12 days ago   ENTRYPOINT ["/docker-entrypoint.sh"]            0B        buildkit.dockerfile.v0
<missing>      12 days ago   COPY 30-tune-worker-processes.sh /docker-ent…   16.4kB    buildkit.dockerfile.v0
<missing>      12 days ago   COPY 20-envsubst-on-templates.sh /docker-ent…   12.3kB    buildkit.dockerfile.v0
<missing>      12 days ago   COPY 15-local-resolvers.envsh /docker-entryp…   12.3kB    buildkit.dockerfile.v0
<missing>      12 days ago   COPY 10-listen-on-ipv6-by-default.sh /docker…   12.3kB    buildkit.dockerfile.v0
<missing>      12 days ago   COPY docker-entrypoint.sh / # buildkit          8.19kB    buildkit.dockerfile.v0
<missing>      12 days ago   RUN /bin/sh -c set -x     && addgroup -g 101…   5.62MB    buildkit.dockerfile.v0
<missing>      12 days ago   ENV DYNPKG_RELEASE=1                            0B        buildkit.dockerfile.v0
<missing>      12 days ago   ENV PKG_RELEASE=1                               0B        buildkit.dockerfile.v0
<missing>      12 days ago   ENV NGINX_VERSION=1.30.5                        0B        buildkit.dockerfile.v0
<missing>      12 days ago   LABEL maintainer=NGINX Docker Maintainers <d…   0B        buildkit.dockerfile.v0
<missing>      2 weeks ago   CMD ["/bin/sh"]                                 0B        buildkit.dockerfile.v0
<missing>      2 weeks ago   ADD alpine-minirootfs-3.24.2-x86_64.tar.gz /…   9.08MB    buildkit.dockerfile.v0
```

Read it from the bottom up: the Alpine base (`ADD alpine-minirootfs…`), then the nginx steps. Only the steps with a
size are file layers; `ENV`, `CMD`, `EXPOSE` and `LABEL` are metadata (`0B`). `<missing>` only means those steps were
built on another machine, so there is no local image ID for them. Count the file layers:

<!-- test: contains=layers; output -->
```bash
echo "$(docker image inspect --format '{{len .RootFS.Layers}}' nginx:1.30-alpine) layers"
```

```text
8 layers
```

The eight sized rows above: one `ADD`, two `RUN`s and five `COPY`s. Each layer is identified by the hash (digest) of
its content, so identical layers are stored only once, whichever images use them.

## Command breakdown

| Command | What it does |
|---|---|
| `docker image history IMAGE` | the build steps of an image, newest first, with the size each one added |
| `--no-trunc` | show the full commands instead of cutting them at `…` |
| `docker image inspect --format '{{.RootFS.Layers}}' IMAGE` | the digests of the file layers, base first |
| `{{len …}}` | Go template: the number of entries in a list |

## Hands-on lab

**Instructions.** Find out how many file layers `python:3.14-slim` has, and which of its steps added the most data.

**Expected result.** A layer count and, near the top of the history, the step that installs Python with tens of MB.

**Verification.**

<!-- test: contains=layers; contains=MB -->
```bash
echo "$(docker image inspect --format '{{len .RootFS.Layers}}' python:3.14-slim) layers"
docker image history --format '{{.Size}}\t{{.CreatedBy}}' python:3.14-slim | sort -h | tail -3
```

## Break it

Build the `broken/` Dockerfile. It creates a 20 MB file in one step and deletes it in the next, hoping to keep the image
small:

<!-- test: contains=layers-demo:broken -->
```bash
cat broken/Dockerfile
docker build -q -t layers-demo:broken broken > /dev/null
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.Size}}' layers-demo
```

The image is about 20 MB bigger than `alpine:3.23`, although the file no longer exists in it:

<!-- test: contains=No such file -->
```bash
docker run --rm layers-demo:broken ls -l /tmp/big.bin 2>&1 || true
```

## Troubleshoot it

The history shows where the space went:

<!-- test: contains=21MB; output -->
```bash
docker image history --format '{{.Size}}\t{{.CreatedBy}}' layers-demo:broken
```

```text
8.19kB	RUN /bin/sh -c rm /tmp/big.bin # buildkit
21MB	RUN /bin/sh -c dd if=/dev/zero of=/tmp/big.b…
0B	CMD ["/bin/sh"]
9.08MB	ADD alpine-minirootfs-3.23.6-x86_64.tar.gz /…
```

The `dd` layer is read-only and permanent: it holds the 20 MB file. The `rm` step cannot change an earlier layer, so it
adds a tiny new layer that only *marks* the file as deleted (a "whiteout"). The container no longer sees the file, but
every pull and every copy of the image still carries the 20 MB.

## Fix it

Create, use and delete temporary files in the **same** step, so they never become part of a layer:

<!-- test: contains=layers-demo:fixed; output -->
```bash
cat fixed/Dockerfile
docker build -q -t layers-demo:fixed fixed > /dev/null
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.Size}}' layers-demo
```

```text
# Create, use and delete the file in the same step: it never reaches a layer
FROM alpine:3.23
RUN dd if=/dev/zero of=/tmp/big.bin bs=1M count=20 \
 && rm /tmp/big.bin
layers-demo:fixed  12.9MB
layers-demo:broken  33.9MB
```

The fixed image is the size of Alpine itself. The same rule applies to package caches (`apt-get install … && rm -rf
/var/lib/apt/lists/*`, `apk add --no-cache`) and downloaded archives (lesson 026). Multi-stage builds (lesson 087) solve
it for whole toolchains.

## Practice challenge

`layers-demo:fixed` and `alpine:3.23` should share their base layer. Prove it by comparing the first layer digest of
both images.

<details>
<summary>Solution</summary>

<!-- test: contains=shared base layer; output -->
```bash
a=$(docker image inspect --format '{{index .RootFS.Layers 0}}' alpine:3.23)
b=$(docker image inspect --format '{{index .RootFS.Layers 0}}' layers-demo:fixed)
echo "alpine: $a"
echo "fixed:  $b"
[ "$a" = "$b" ] && echo "shared base layer: stored once on disk"
```

```text
alpine: sha256:e63b02c2b5c761df2cb95e657d744f27d95da4e051235a13c80b88cd68eab188
fixed:  sha256:e63b02c2b5c761df2cb95e657d744f27d95da4e051235a13c80b88cd68eab188
shared base layer: stored once on disk
```

`index LIST 0` takes the first entry: the base layer. Same content, same digest, one copy on disk; a registry also
stores it once and a pull skips layers that are already present.

</details>

## Real-world example

A team builds 30 services on the same company base image. Because every service image starts with the same base
layers, a server that runs all 30 downloads and stores the base only once, and a new release of a service only pulls
the few top layers that changed. When an image suddenly grows by hundreds of MB, `docker image history` points to the
step responsible in seconds, typically a cache or an archive that was deleted in a later step.

## Recap

- An image is a stack of read-only layers; `RUN`, `COPY` and `ADD` create layers, other instructions only metadata.
- A container adds a thin writable layer on top.
- Layers are content-addressed (digests) and shared between images: stored, pushed and pulled once.
- Deleting a file in a later layer hides it but does not shrink the image: create and delete in the same step.

## Cleanup

<!-- test -->
```bash
docker image rm -f layers-demo:broken layers-demo:fixed > /dev/null
rm -rf ~/docker-practice/lesson-017
```

Next: [Lesson 018 · Pulling images](../018-pulling-images/README.md)
