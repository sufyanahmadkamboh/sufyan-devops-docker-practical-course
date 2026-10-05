<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 017 · Image layers · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Build the `broken/` Dockerfile. It creates a 20 MB file in one step and deletes it in the next, hoping to keep the image
small:

```bash
cat broken/Dockerfile
docker build -q -t layers-demo:broken broken > /dev/null
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.Size}}' layers-demo
```

The image is about 20 MB bigger than `alpine:3.23`, although the file no longer exists in it:

```bash
docker run --rm layers-demo:broken ls -l /tmp/big.bin 2>&1 || true
```

## Troubleshoot it

The history shows where the space went:

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
