# Troubleshooting problem 17 · Unexpected cache

> ⏱ 15 minutes · run every command from the course folder · related lessons: 038, 039, 105

## Problem

The pricing image downloads the latest exchange rates during the build. A new build was made this morning, yet the
image still contains yesterday's rates. The build succeeded and printed no error.

## Symptoms

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh trouble-17 17-troubleshooting/17-unexpected-cache/examples
cd ~/docker-practice/trouble-17
docker build -q -t pricing:monday broken > /dev/null
docker run --rm pricing:monday
```

Some time later, a new build:

<!-- test: contains=fetched at; output -->
```bash
sleep 3
docker build -q -t pricing:tuesday broken > /dev/null
docker run --rm pricing:monday
docker run --rm pricing:tuesday
```

```text
exchange rates fetched at 10:27:28
exchange rates fetched at 10:27:28
```

The same time in both images: the "fresh" build contains the old download.

## Investigation

**1. Did the build run the step at all?** The build output marks reused steps as `CACHED`:

<!-- test: contains=CACHED; output -->
```bash
docker build --progress=plain -t pricing:tuesday broken 2>&1 | grep -E '^#[0-9]+ \[|CACHED'
```

```text
#1 [internal] load build definition from Dockerfile
#2 [internal] load metadata for docker.io/library/alpine:3.23
#3 [internal] load .dockerignore
#4 [internal] load build context
#5 [1/3] FROM docker.io/library/alpine:3.23@sha256:85fe1e81d6758c208f3e1eed4338a1997e19d4be002d4dd32d3100c9a8c010a0
#6 [2/3] RUN echo "exchange rates fetched at $(date -u +%H:%M:%S)" > /rates.txt
#6 CACHED
#7 [3/3] COPY show-rates.sh /show-rates.sh
#7 CACHED
```

**2. Do the two images contain the same layers?** The layer digests identify the file system content:

<!-- test: contains=same layers; output -->
```bash
[ "$(docker image inspect --format '{{json .RootFS.Layers}}' pricing:monday)" = "$(docker image inspect --format '{{json .RootFS.Layers}}' pricing:tuesday)" ]   && echo "same layers: nothing was rebuilt"
```

```text
same layers: nothing was rebuilt
```

## Commands

| Command | What it tells you |
|---|---|
| `docker build --progress=plain .` | every step, with `CACHED` for each step that was reused |
| `docker image inspect --format '{{json .RootFS.Layers}}'` | whether two images contain the same layers |
| `docker history IMAGE` | when each layer was really created |
| `docker build --no-cache .` | rebuild everything (slow, for diagnosis and scheduled builds) |

## Output interpretation

The cache key of a `RUN` step is its **command text** and the layer before it, never the result (lesson 039). The
command `echo … $(date …)` (or `curl https://…/rates.json`, `apk upgrade`) did not change, the base layer did not
change, so BuildKit reused the layer from the first build without running anything. For `COPY`, the key includes the
copied files' contents, which is why changing `show-rates.sh` would rebuild from that step on, but never the step
before it.

## Root cause

A build step that depends on something outside the build context (the network, the time, a remote repository) was
cached: Docker cannot know that its result would be different now.

## Fix

Make the dependency part of the cache key. A build argument used by the step invalidates it whenever its value
changes:

<!-- test: contains=ARG RATES_VERSION; output -->
```bash
grep -n 'ARG\|RUN' fixed/Dockerfile
```

```text
4:ARG RATES_VERSION=unset
5:RUN echo "exchange rates fetched at $(date -u +%H:%M:%S) (rates version $RATES_VERSION)" > /rates.txt
```

<!-- test -->
```bash
docker build -q --build-arg RATES_VERSION=2026-10-05 -t pricing:fixed fixed > /dev/null
```

## Verification

The same value reuses the cache (fast, reproducible); a new value runs the download again:

<!-- test: contains=rates version 2026-10-05; contains=rates version 2026-10-06; output -->
```bash
docker run --rm pricing:fixed
sleep 2
docker build -q --build-arg RATES_VERSION=2026-10-06 -t pricing:fixed fixed > /dev/null
docker run --rm pricing:fixed
```

```text
exchange rates fetched at 10:27:36 (rates version 2026-10-05)
exchange rates fetched at 10:27:40 (rates version 2026-10-06)
```

## Prevention

- Never rely on the cache for freshness: pin what you download (a version, a checksum) so the Dockerfile changes when
  the content should.
- Rebuild regularly without cache, and with `--pull` to get the patched base image: a nightly or weekly
  `docker build --pull --no-cache` in CI (lesson 137).
- The opposite surprise (the cache is never used, every build is slow) comes from `COPY . .` before installing
  dependencies: [lesson 105](../../16-advanced/105-cache-optimization/README.md).

## Cleanup

<!-- test -->
```bash
docker image rm pricing:monday pricing:tuesday pricing:fixed > /dev/null
rm -rf ~/docker-practice/trouble-17
```

Next: [Problem 18 · Huge image](../18-huge-image/README.md)
