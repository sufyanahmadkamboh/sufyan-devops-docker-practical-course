# Troubleshooting problem 25 · Image pull failure

> ⏱ 20 minutes · run every command from the course folder · related lessons: 018, 020, 076, 078

## Problem

Three reports in one morning: a new server cannot start the proxy (`pull access denied`), a CI job cannot find its
base image (`not found`), and a training room full of laptops gets `toomanyrequests` / `429 Too Many Requests` for
images that certainly exist.

## Symptoms

**A misspelled repository** (`ngnix` instead of `nginx`):

<!-- test: fail; anyof=pull access denied||429 Too Many Requests||toomanyrequests; output -->
```bash
docker pull ngnix:1.30-alpine 2>&1
```

```text
Error response from daemon: pull access denied for ngnix, repository does not exist or may require 'docker login'
```

**A tag that does not exist:**

<!-- test: fail; anyof=not found||manifest unknown||429 Too Many Requests||toomanyrequests; output -->
```bash
docker pull nginx:9.99-alpine 2>&1
```

```text
Error response from daemon: failed to resolve reference "docker.io/library/nginx:9.99-alpine": docker.io/library/nginx:9.99-alpine: not found
```

**The rate limit.** Docker Hub limits how many pulls an anonymous client (counted per public IP address) may make in a
period; a classroom, an office behind one NAT address or a busy CI runner reaches it quickly. Then every request is
answered with `429 Too Many Requests` (as a pull: `toomanyrequests: You have reached your unauthenticated pull rate
limit`), whether the image exists or not. If the outputs above say 429, you are seeing it right now.

## Investigation

**1. Is the image already here?** Docker only contacts the registry when the image is missing locally (or on an
explicit `docker pull`):

<!-- test: contains=nginx:1.30-alpine; output -->
```bash
docker image ls --format '{{.Repository}}:{{.Tag}}' | grep -E '^(nginx|ngnix):' || echo "no image named like nginx/ngnix"
```

```text
nginx:1.30-alpine
nginx:1.29-alpine
```

**2. Read the reference carefully.** `ngnix:1.30-alpine` means `docker.io/library/ngnix:1.30-alpine`: registry
`docker.io`, namespace `library` (official images), repository `ngnix`. "Repository does not exist or may require
docker login" is deliberately vague: registries do not reveal whether a private repository exists.

**3. Ask the registry how much of the limit is left.** Docker Hub reports it in response headers. Get an anonymous
token, then send a `HEAD` request (the documented way to check without pulling):

<!-- test: anyof=ratelimit-limit||429; output -->
```bash
token=$(curl -s "https://auth.docker.io/token?service=registry.docker.io&scope=repository:ratelimitpreview/test:pull" | sed 's/.*"token":"\([^"]*\)".*/\1/')
curl -sI -H "Authorization: Bearer $token" https://registry-1.docker.io/v2/ratelimitpreview/test/manifests/latest \
  | grep -iE '^HTTP|^ratelimit' || true
```

```text
HTTP/1.1 200 OK
ratelimit-limit: 100;w=3600
ratelimit-remaining: 100;w=3600
```

`ratelimit-limit: N;w=S` reads "N pulls per window of S seconds"; `ratelimit-remaining` is what is left for your
IP address. An `HTTP/1.1 429` line means the limit is used up. The numbers are Docker Hub's policy of the day and
change over time.

## Commands

| Command | What it tells you |
|---|---|
| `docker image ls` / `docker image inspect IMAGE` | whether the image is already local (no registry needed) |
| `docker pull IMAGE 2>&1 \| tail -1` | the registry's answer: denied, not found, 429 |
| `curl -sI … /v2/ratelimitpreview/test/manifests/latest` | Docker Hub's rate limit and remaining pulls |
| `docker info --format '{{.RegistryConfig.Mirrors}}'` | the mirrors this engine uses |

## Output interpretation

| Message | Cause | Fix |
|---|---|---|
| `pull access denied … repository does not exist or may require 'docker login'` | typo in the name, or a private repository | fix the name, or log in |
| `manifest unknown` / `not found` | the tag does not exist (or not for your platform) | check the tags on the registry |
| `429 Too Many Requests` / `toomanyrequests` | rate limit reached | log in, use a mirror, cache images |
| `unauthorized: authentication required` | private image, not logged in | [problem 24](../24-registry-authentication-failure/README.md) |
| `dial tcp … i/o timeout`, `no such host` | no network or DNS to the registry | proxy, DNS, firewall settings |

## Root cause

1. A typo in the repository name: `ngnix`.
2. A tag that was never published: `9.99-alpine`.
3. Too many anonymous pulls from one IP address: Docker Hub's rate limit.

## Fix

**Typos:** use the exact reference from the registry's tag list, and pin it (lesson 020). The correct image is already
local, so it runs without contacting the registry:

<!-- test: contains=nginx version; output -->
```bash
docker run --rm --entrypoint nginx nginx:1.30-alpine -v 2>&1
```

```text
nginx version: nginx/1.30.5
```

**Rate limit, option 1: log in.** Authenticated users get a higher limit (a free account is enough). Use an access
token, not your password:

<!-- test: skip -->
```bash
docker login -u YOUR_DOCKER_HUB_USER        # paste an access token when asked for the password
```

**Option 2: a mirror.** Google runs a public pull-through cache of Docker Hub's official images at `mirror.gcr.io`.
Pull from it, then give the image its usual name:

<!-- test: contains=nginx:1.30-alpine; output -->
```bash
docker pull -q mirror.gcr.io/library/nginx:1.30-alpine
docker tag mirror.gcr.io/library/nginx:1.30-alpine nginx:1.30-alpine
docker image rm mirror.gcr.io/library/nginx:1.30-alpine > /dev/null
docker image ls nginx:1.30-alpine --format '{{.Repository}}:{{.Tag}}  {{.ID}}'
```

```text
mirror.gcr.io/library/nginx:1.30-alpine
nginx:1.30-alpine  0985e772fb9f
```

The course's `bash scripts/prefetch-images.sh --mirror` does this for every image of the course. To make the engine
use a mirror for **every** Docker Hub pull, add it to the daemon configuration (Docker Desktop: *Settings → Docker
Engine*; Linux: `/etc/docker/daemon.json`, then restart Docker). The CI workflow of this course does exactly that:

<!-- test: skip -->
```json
{
  "registry-mirrors": ["https://mirror.gcr.io"]
}
```

**Option 3: pull less.** Reuse cached images (`docker run` does not pull when the image is local), and in a team run
your own pull-through cache or copy base images into your company registry (lesson 078).

## Verification

<!-- test: contains=nginx/1.30; output -->
```bash
docker run -d --name proxy -p 8080:80 nginx:1.30-alpine > /dev/null
sleep 1
curl -sI http://localhost:8080 | grep -i '^server'
```

```text
Server: nginx/1.30.5
```

## Prevention

- Pin exact image references (`nginx:1.30-alpine`, or a digest) and copy them from the registry, not from memory.
- Log in to Docker Hub in CI and on servers, with a read-only access token.
- Configure a registry mirror or a pull-through cache for teams, classrooms and CI runners.
- Do not `docker pull` images that are already local in scripts that run often: check with
  `docker image inspect IMAGE > /dev/null 2>&1 || docker pull IMAGE`.

## Cleanup

<!-- test -->
```bash
docker rm -f proxy > /dev/null
```

Next: [Troubleshooting index](../README.md)
