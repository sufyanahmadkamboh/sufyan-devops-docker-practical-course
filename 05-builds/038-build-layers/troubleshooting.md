<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 038 · Build layers · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A Dockerfile that "cleans up" in a separate step (`Dockerfile.wasteful`):

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

```bash
docker run --rm layers:wasteful ls /tmp/download.bin 2>&1 || true
```

But the history shows where the space went:

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
