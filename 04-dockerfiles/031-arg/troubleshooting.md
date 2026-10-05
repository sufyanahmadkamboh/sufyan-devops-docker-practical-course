<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 031 · ARG · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A colleague moves `ARG VERSION` to the top of the file, next to the other argument:

```bash
cat > Dockerfile.scope <<'EOF'
ARG ALPINE_VERSION=3.23
ARG VERSION=dev
FROM alpine:${ALPINE_VERSION}
RUN echo "version [$VERSION]" > /version
CMD ["cat", "/version"]
EOF
docker build -q -f Dockerfile.scope --build-arg VERSION=1.4.0 -t menu-arg:scope . > /dev/null
docker run --rm menu-arg:scope
```

```text
version []
```

The build succeeded, and the version is empty, although `--build-arg VERSION=1.4.0` was given.

## Troubleshoot it

An `ARG` declared **before** `FROM` belongs to the "global" scope: it can be used in `FROM` lines only. Each `FROM`
starts a new build stage, and inside a stage an argument exists only after an `ARG` line in that stage. The history of
the image shows which arguments the `RUN` step received:

```bash
docker image history --no-trunc --format '{{.CreatedBy}}' menu-arg:scope | grep '^RUN'
```

```text
RUN /bin/sh -c echo "version [$VERSION]" > /version # buildkit
```

No arguments (compare the fixed version below, which records `RUN |1 VERSION=1.4.0 …`).

## Fix it

Declare it again inside the stage (without a value, it keeps the global default or the `--build-arg` value):

```bash
awk '{ print } /^FROM / { print "ARG VERSION" }' Dockerfile.scope > Dockerfile.tmp && mv Dockerfile.tmp Dockerfile.scope
cat Dockerfile.scope
docker build -q -f Dockerfile.scope --build-arg VERSION=1.4.0 -t menu-arg:scope . > /dev/null
docker run --rm menu-arg:scope
docker image history --no-trunc --format '{{.CreatedBy}}' menu-arg:scope | grep '^RUN'
```

```text
ARG ALPINE_VERSION=3.23
ARG VERSION=dev
FROM alpine:${ALPINE_VERSION}
ARG VERSION
RUN echo "version [$VERSION]" > /version
CMD ["cat", "/version"]
version [1.4.0]
RUN |1 VERSION=1.4.0 /bin/sh -c echo "version [$VERSION]" > /version # buildkit
```

That last line is why `ARG` is not for secrets: **every value a `RUN` step uses is written into the image's history**.
Anyone who can pull the image can read it with `docker image history --no-trunc`.
