<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 105 · Build cache optimization · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A teammate adds the build time to the image, at the top of the Dockerfile where it is easy to find. CI passes the time
on every build:

```bash
head -4 Dockerfile.broken
```

```text
FROM python:3.14-slim
# build metadata, added "at the top, where it is easy to find"
ARG BUILD_TIME
RUN echo "built at ${BUILD_TIME}" > /build-info.txt
```

```bash
sh build-steps.sh -f Dockerfile.broken --build-arg BUILD_TIME=1001 -t cafe-api:broken . > /dev/null
sh build-steps.sh -f Dockerfile.broken --build-arg BUILD_TIME=1002 -t cafe-api:broken .
```

```text
base   [1/6] FROM docker.io/library/python:3.14-slim@sha256:c3e521df8b2b498a7
ran    [2/6] RUN echo "built at 1002" > /build-info.txt
ran    [3/6] WORKDIR /app
ran    [4/6] COPY requirements.txt .
ran    [5/6] RUN --mount=type=cache,target=/root/.cache/pip pip install -r re
ran    [6/6] COPY . .
```

Nothing changed in the code or the dependencies, but almost every step ran again.

## Troubleshoot it

Find the **first** step that ran; everything after it runs because of it. Here it is step 2: `RUN echo "built at
${BUILD_TIME}"`. An `ARG` value is part of the cache key of every `RUN` step after its declaration, because those steps
can read it as an environment variable. A new value on every build = a cache miss on every build from there on.

The same diagnosis applies to other cache busters: a `COPY . .` early in the file, a file that changes on every build
(a log, a timestamp, `.git/`) in the build context, or `--no-cache` left in a script.

## Fix it

Declare the changing value as late as possible, and use it only where it is needed (a label, see `Dockerfile.fixed`):

```bash
sh build-steps.sh -f Dockerfile.fixed --build-arg BUILD_TIME=1001 -t cafe-api:fixed . > /dev/null
sh build-steps.sh -f Dockerfile.fixed --build-arg BUILD_TIME=1002 -t cafe-api:fixed .
docker image inspect --format '{{index .Config.Labels "org.opencontainers.image.created"}}' cafe-api:fixed
```

```text
base   [1/5] FROM docker.io/library/python:3.14-slim@sha256:c3e521df8b2b498a7
cached [2/5] WORKDIR /app
cached [3/5] COPY requirements.txt .
cached [4/5] RUN --mount=type=cache,target=/root/.cache/pip pip install -r re
cached [5/5] COPY . .
1002
```

Every step is cached; only the label (metadata, no layer) changed.
