# Lesson 038 · Build layers

> Level 6 · Docker builds · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

Every `RUN`, `COPY` and `ADD` instruction produces a **layer**: the set of files that step added, changed or deleted.
An image is its base image's layers plus one layer per such instruction, stacked; other instructions (`WORKDIR`,
`CMD`, `ENV`, `EXPOSE`) only change metadata. Layers are **immutable**: a later step can hide a file, but never remove
it from an earlier layer. That is why the way you split a Dockerfile into steps decides how big the image is.

## Visual

```text
  Dockerfile.wasteful                       image layers (each one is stored and pulled)

  FROM alpine:3.23                    ──▶   base layer                          9 MB
  RUN head -c 30000000 … > download   ──▶   + /tmp/download.bin                30 MB
  RUN sha256sum … > /checksum.txt     ──▶   + /checksum.txt                   < 1 kB
  RUN rm /tmp/download.bin            ──▶   "whiteout": hide download.bin    ≈ 8 kB
                                            ─────────────────────────────────────────
                                            total (unpacked)                  ≈ 39 MB   (the 30 MB are still there)

  Dockerfile.fixed
  FROM alpine:3.23                    ──▶   base layer                          9 MB
  RUN download && checksum && rm      ──▶   + /checksum.txt only              < 1 kB
                                            total                             ≈  9 MB
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-038 05-builds/038-build-layers/examples
cd ~/docker-practice/lesson-038
cat Dockerfile
```

## Demonstration

Build the image and list its layers with `docker history`, newest first:

<!-- test: contains=apk add; output -->
```bash
docker build -q -t layers:demo . > /dev/null
docker history --format '{{.Size}}\t{{.CreatedBy}}' layers:demo
```

```text
0B	CMD ["sh" "hello.sh"]
12.3kB	COPY hello.sh . # buildkit
8.19kB	WORKDIR /app
5.4MB	RUN /bin/sh -c apk add --no-cache curl # bui…
0B	CMD ["/bin/sh"]
9.08MB	ADD alpine-minirootfs-3.23.6-x86_64.tar.gz /…
```

Read it bottom-up: the two Alpine lines are the base image's own history, then one line per instruction of our
Dockerfile. `apk add curl` added about 5 MB; `COPY hello.sh` a few kB; `CMD` is metadata only (0 B).

<!-- test: contains=curl is curl; output -->
```bash
docker run --rm layers:demo
```

```text
curl is curl 8.22.0
```

## Command breakdown

| Command | What it shows |
|---|---|
| `docker history IMAGE` | every layer: the instruction that created it and its size |
| `--format '{{.Size}}\t{{.CreatedBy}}'` | only those two columns (`--no-trunc` shows full commands) |
| `docker image ls IMAGE` | the total size of the image |
| `docker image inspect --format '{{len .RootFS.Layers}}' IMAGE` | how many file system layers the image has |

## Hands-on lab

**Instructions.** Count the file system layers of `layers:demo` and of its base image `alpine:3.23`. How many layers did
our Dockerfile add?

**Expected result.** Alpine has 1 layer; `layers:demo` has 4: `RUN`, `WORKDIR` and `COPY` each added one (BuildKit
records `WORKDIR` as a small layer because it creates the folder).

**Verification.**

<!-- test: contains=layers:demo 4 -->
```bash
for image in alpine:3.23 layers:demo; do
  echo "$image $(docker image inspect --format '{{len .RootFS.Layers}}' "$image")"
done
```

## Break it

A Dockerfile that "cleans up" in a separate step (`Dockerfile.wasteful`):

<!-- test: contains=layers:wasteful; output -->
```bash
cat Dockerfile.wasteful
docker build -q -f Dockerfile.wasteful -t layers:wasteful . > /dev/null
docker image ls layers:wasteful
```

```text
FROM alpine:3.23
# download a 30 MB archive, compute its checksum, then "clean up"
RUN head -c 30000000 /dev/urandom > /tmp/download.bin
RUN sha256sum /tmp/download.bin > /checksum.txt
RUN rm /tmp/download.bin
IMAGE             ID             DISK USAGE   CONTENT SIZE   EXTRA
layers:wasteful   1777106ec849         73MB         33.9MB        
```

The file was deleted, yet the image is about 30 MB bigger than Alpine.

## Troubleshoot it

The file is gone from the container's view:

<!-- test: contains=No such file -->
```bash
docker run --rm layers:wasteful ls /tmp/download.bin 2>&1 || true
```

But the history shows where the space went:

<!-- test: contains=download.bin; output -->
```bash
docker history --format '{{.Size}}\t{{.CreatedBy}}' layers:wasteful | head -3
```

```text
8.19kB	RUN /bin/sh -c rm /tmp/download.bin # buildk…
8.19kB	RUN /bin/sh -c sha256sum /tmp/download.bin >…
30MB	RUN /bin/sh -c head -c 30000000 /dev/urandom…
```

The 30 MB layer is still part of the image; the `rm` step only added a tiny layer containing a "whiteout" marker
that hides the file from the layers above. Everyone who pulls the image downloads those 30 MB (and anyone can extract the "deleted" file from
the layer, which matters a lot for secrets: lesson 083).

## Fix it

Create, use and delete temporary files in the **same** `RUN`, so the file never exists at the end of any layer:

<!-- test: contains=layers:fixed; output -->
```bash
docker build -q -f Dockerfile.fixed -t layers:fixed . > /dev/null
docker image ls layers
```

```text
IMAGE             ID             DISK USAGE   CONTENT SIZE   EXTRA
layers:demo       d9ad4b5642c1       20.8MB         6.34MB        
layers:fixed      0ba00218b504       12.9MB         3.85MB        
layers:wasteful   1777106ec849         73MB         33.9MB        
```

The same work, with the 30 MB gone. The same rule explains `apk add --no-cache` and
`apt-get update && apt-get install … && rm -rf /var/lib/apt/lists/*` in one `RUN`: package indexes never land in a
layer. Multi-stage builds (lesson 087) go one step further: the build tools stay in a stage that is not shipped at all.

## Practice challenge

Using only `docker history`, find the single largest layer of `node:24-alpine` and the instruction that created it.

<details>
<summary>Solution</summary>

<!-- test: contains=node; output -->
```bash
docker history --no-trunc --format '{{.Size}}\t{{.CreatedBy}}' node:24-alpine | sort -h | tail -1 | cut -c1-90
```

```text
165MB	RUN /bin/sh -c addgroup -g 1000 node     && adduser -u 1000 -G node -s /bin/sh -D no
```

`sort -h` sorts human-readable sizes (kB, MB, GB). The biggest layer installs Node.js itself; it starts with
creating the `node` user, which is why the command shows `addgroup` first.

</details>

## Real-world example

A team's CI image is 2.1 GB and slow to pull on every job. `docker history` shows a 900 MB layer from
`RUN apt-get install …` followed by a 0 B `RUN apt-get clean`: the cleanup ran in a separate step and freed nothing.
Merging the two into one `RUN` (and adding `--no-install-recommends`) is often the single biggest size win in a
Dockerfile review. Measure before and after with `docker image ls`, never guess.

## Recap

- `RUN`, `COPY` and `ADD` each add a layer; other instructions are metadata.
- Layers are immutable: deleting a file in a later step hides it but does not shrink the image.
- Create, use and delete temporary files in one `RUN`.
- `docker history` shows every layer and its size; use it to find what makes an image big.

## Cleanup

<!-- test -->
```bash
docker image rm -f layers:demo layers:wasteful layers:fixed > /dev/null
rm -rf ~/docker-practice/lesson-038
```

Next: [Lesson 039 · The build cache](../039-build-cache/README.md)
