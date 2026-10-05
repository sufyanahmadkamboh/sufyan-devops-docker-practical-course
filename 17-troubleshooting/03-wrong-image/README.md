# Troubleshooting problem 03 · Wrong image

> ⏱ 15 minutes · run every command from the course folder · related lessons: 016, 020, 021, 101

## Problem

Version 2.0 of the price list was built and "deployed", yet users still see version 1.0. The container runs, the
logs are clean, and there is no error anywhere: the container simply runs a different image than everyone believes.

## Symptoms

Reproduce the release history: version 1.0 was built and also tagged `latest`; version 2.0 was built later, with its
own tag only. The deployment command uses the image name without a tag.

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh trouble-03 17-troubleshooting/03-wrong-image/examples
cd ~/docker-practice/trouble-03
docker build -q --build-arg VERSION=1.0 -t price-list:1.0 -t price-list:latest . > /dev/null
docker build -q --build-arg VERSION=2.0 -t price-list:2.0 . > /dev/null
docker run -d --name prices -p 8080:8080 price-list > /dev/null
```

<!-- test: retry=10; contains=version 1.0; output -->
```bash
curl -s http://localhost:8080
```

```text
price-list version 1.0
```

## Investigation

**1. Which image does the container run?** `docker ps` shows the name it was started with, not what that name meant:

<!-- test: contains=price-list; output -->
```bash
docker ps --filter name=prices --format '{{.Names}}: {{.Image}}'
docker inspect --format 'configured image: {{.Config.Image}}  image ID: {{.Image}}' prices
```

```text
prices: price-list
configured image: price-list  image ID: sha256:dd2c46cf131277d11781a0866f368fc8b21ee299a2f3ec823c436d2022aa95b4
```

**2. Which tags point to that image ID?**

<!-- test: contains=price-list:latest; output -->
```bash
docker image ls price-list --format '{{.Repository}}:{{.Tag}}  {{.ID}}  {{.CreatedSince}}'
```

```text
price-list:2.0  a38a887d60b9  2 seconds ago
price-list:1.0  dd2c46cf1312  3 seconds ago
price-list:latest  dd2c46cf1312  3 seconds ago
```

`latest` and `1.0` share one ID; `2.0` has another. `price-list` without a tag means `price-list:latest`, and `latest`
was never moved to 2.0.

**3. Read the version from the image's metadata** (lesson 101), instead of trusting the tag:

<!-- test: contains=1.0; output -->
```bash
docker inspect --format '{{index .Config.Labels "org.opencontainers.image.version"}}' prices
```

```text
1.0
```

## Commands

| Command | What it tells you |
|---|---|
| `docker inspect --format '{{.Config.Image}}' NAME` | the image reference the container was started with |
| `docker inspect --format '{{.Image}}' NAME` | the exact image ID it runs |
| `docker image ls REPO --format '{{.Tag}} {{.ID}}'` | which tags point to which ID |
| `docker inspect --format '{{index .Config.Labels "…"}}'` | metadata written at build time (version, Git commit) |

## Output interpretation

A tag is a movable pointer to an image ID, nothing more (lesson 020). `latest` is not "the newest": it is whatever
was last tagged `latest`, and `docker run price-list` silently means `price-list:latest` (lesson 021). Only the image
ID (or the digest of a pushed image) identifies an image for certain.

## Root cause

The deployment referenced `price-list` (implicitly `:latest`), which still pointed to the 1.0 build. Nothing was
broken technically: the wrong image was chosen.

## Fix

Deploy an explicit version tag:

<!-- test -->
```bash
docker rm -f prices > /dev/null
docker run -d --name prices -p 8080:8080 price-list:2.0 > /dev/null
```

## Verification

<!-- test: retry=10; contains=version 2.0; output -->
```bash
curl -s http://localhost:8080
docker inspect --format 'runs {{.Config.Image}}, label version {{index .Config.Labels "org.opencontainers.image.version"}}' prices
```

```text
price-list version 2.0
runs price-list:2.0, label version 2.0
```

## Prevention

- Never deploy `latest`. Deploy an immutable version tag (`2.0`, `2.0.3`, a Git commit SHA) or a digest
  (`price-list@sha256:…`, lesson 077).
- Write the version and the Git commit into labels at build time (`LABEL org.opencontainers.image.version=…`) and
  check them after a deployment.
- In CI, tag every build with the commit SHA, so every running container can be traced to its source (lesson 136).
- A related case: the right name for the wrong *platform* (an `arm64` image on an `amd64` server) fails with
  `exec format error` (lesson 104).

## Cleanup

<!-- test -->
```bash
docker rm -f prices > /dev/null
docker image rm price-list:1.0 price-list:latest price-list:2.0 > /dev/null
rm -rf ~/docker-practice/trouble-03
```

Next: [Problem 04 · Port already in use](../04-port-already-in-use/README.md)
