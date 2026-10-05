# Lesson 018 · Pulling images

> Level 4 · Images · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

`docker image pull` downloads an image from a **registry**. Every image name is really a full address,
`REGISTRY/NAMESPACE/REPOSITORY:TAG`, and Docker fills in what you leave out: `alpine:3.23` means
`docker.io/library/alpine:3.23`. A pull downloads only the layers you do not have yet. A **tag** can move to a new
image; a **digest** (`@sha256:…`) always means exactly the same bytes.

## Visual

```text
   docker image pull alpine:3.23
                     │  expands to
                     ▼
   docker.io / library / alpine : 3.23           mirror.gcr.io / library / busybox : 1.37
   ─────────   ───────   ──────   ────           ─────────────   ───────   ───────   ────
   registry    namespace  repo     tag            another registry, same naming rules

   client ──▶ dockerd ──▶ registry: "manifest for alpine:3.23?"
                     ◀── manifest: digest sha256:85fe…, layers L1 L2 …
                     ──▶ download only the layers not already on disk
   result:   tag  alpine:3.23  ──▶ digest sha256:85fe…  (a tag can be moved to a newer image; a digest cannot)
```

## Lab setup

No files are needed. The course's images were downloaded by `scripts/prefetch-images.sh` (lesson 001).

## Demonstration

Show the images you have, with the digest each tag currently points to:

<!-- test: contains=DIGEST -->
```bash
docker image ls --digests alpine
```

Pull an image you already have. Docker asks the registry whether the tag still points to the same digest:

<!-- test: anyof=Image is up to date||429 Too Many Requests||toomanyrequests; output -->
```bash
docker image pull alpine:3.23 2>&1 || echo "the pull failed: read the error above"
```

```text
3.23: Pulling from library/alpine
Digest: sha256:85fe1e81d6758c208f3e1eed4338a1997e19d4be002d4dd32d3100c9a8c010a0
Status: Image is up to date for alpine:3.23
docker.io/library/alpine:3.23
```

Two results are possible, and both are useful to recognise:

- `Status: Image is up to date for alpine:3.23`: the tag still points to the digest you have; nothing was downloaded.
- `429 Too Many Requests` (or `toomanyrequests: You have reached your unauthenticated pull rate limit`): Docker Hub
  limits how many requests an anonymous user (an IP address) can make in a time window. Even a pull of an image you
  already have counts, because Docker must ask the registry. Logging in (`docker login`, lesson 076) raises the limit;
  a mirror or your own registry avoids it.

Images do not have to come from Docker Hub. Pull the same BusyBox from Google's public mirror of Docker Hub:

<!-- test: contains=mirror.gcr.io/library/busybox:1.37; output -->
```bash
docker image pull mirror.gcr.io/library/busybox:1.37
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.ID}}' | grep busybox
```

```text
1.37: Pulling from library/busybox
Digest: sha256:bdf57e528e45e4433820e045b29b4597825a1c9e38353532d90a01445013f82e
Status: Downloaded newer image for mirror.gcr.io/library/busybox:1.37
mirror.gcr.io/library/busybox:1.37
mirror.gcr.io/library/busybox:1.37  bdf57e528e45
busybox:1.37  bdf57e528e45
```

Same image ID: the bytes are identical, only the name is different, and the layers that were already on disk were not
downloaded again.

Run an image by its **digest** instead of its tag:

<!-- test: contains=3.23; output -->
```bash
digest=$(docker image inspect --format '{{index .RepoDigests 0}}' alpine:3.23)
echo "$digest"
docker run --rm "$digest" cat /etc/alpine-release
```

```text
alpine@sha256:85fe1e81d6758c208f3e1eed4338a1997e19d4be002d4dd32d3100c9a8c010a0
3.23.6
```

## Command breakdown

| Command / part | Meaning |
|---|---|
| `docker image pull NAME:TAG` | download an image (`docker pull` is the short form) |
| `docker.io/library/` | the default registry and namespace of official images, added when you omit them |
| `-q` | quiet: print only the image name |
| `--platform linux/arm64` | pull the variant for another CPU architecture (lesson 104) |
| `docker image ls --digests` | show the digest each local tag refers to |
| `NAME@sha256:…` | an image by digest: immutable, always the same content |

## Hands-on lab

**Instructions.** Pull `alpine:3.23` from `mirror.gcr.io` (the official images are under `library/`), show that it has
the same ID as your `alpine:3.23`, then remove only the mirror's name.

**Expected result.** Both names list the same image ID; after the removal, `alpine:3.23` is still there.

**Verification.**

<!-- test: contains=Untagged: mirror.gcr.io/library/alpine:3.23; contains=alpine:3.23 -->
```bash
docker image pull -q mirror.gcr.io/library/alpine:3.23
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.ID}}' | grep alpine
docker image rm mirror.gcr.io/library/alpine:3.23
docker image ls --format '{{.Repository}}:{{.Tag}}' alpine
```

`Untagged` (not `Deleted`): the image is still used by the name `alpine:3.23`, so only the name is removed.

## Break it

Pull an image name that does not exist:

<!-- test: fail; anyof=repository does not exist||429 Too Many Requests||toomanyrequests; output -->
```bash
docker image pull cafe-menu-api:1.0 2>&1
```

```text
Error response from daemon: pull access denied for cafe-menu-api, repository does not exist or may require 'docker login'
```

## Troubleshoot it

`pull access denied … repository does not exist or may require 'docker login'`: Docker expanded the name to
`docker.io/library/cafe-menu-api:1.0`, and Docker Hub refused it. The registry deliberately gives the same answer for
"does not exist" and "exists but is private", so you check both:

1. **The name.** Is it spelled correctly, with the right namespace? Your team's image is probably
   `docker.io/yourteam/cafe-menu-api` or on another registry (`ghcr.io/yourteam/cafe-menu-api`), not an official
   `library/` image.
2. **The tag.** A wrong tag on an existing repository gives `manifest unknown` / `not found` instead.
3. **Access.** A private repository needs `docker login REGISTRY` first (lesson 076).
4. **The rate limit.** `429 Too Many Requests` is not about the name at all: wait, log in, or use a mirror.

Check what the name expands to and whether such an image exists locally:

<!-- test: contains=no local image -->
```bash
docker image inspect docker.io/library/cafe-menu-api:1.0 > /dev/null 2>&1 || echo "no local image docker.io/library/cafe-menu-api:1.0"
```

## Fix it

Use the full, correct name. A safe pattern for scripts pulls only when the image is missing, so it does not spend a
registry request (or fail on a rate limit) when the image is already there:

<!-- test: contains=busybox ready -->
```bash
docker image inspect busybox:1.37 > /dev/null 2>&1 || docker image pull busybox:1.37
echo "busybox ready: $(docker image inspect --format '{{.Id}}' busybox:1.37 | cut -c1-19)"
```

## Practice challenge

Show that `alpine:3.23`, `docker.io/library/alpine:3.23` and `alpine@sha256:…` (its digest) are three names for the
same image, without contacting any registry.

<details>
<summary>Solution</summary>

<!-- test: contains=same image; output -->
```bash
digest=$(docker image inspect --format '{{index .RepoDigests 0}}' alpine:3.23)
for name in alpine:3.23 docker.io/library/alpine:3.23 "$digest"; do
  docker image inspect --format '{{.Id}}' "$name"
done | sort -u | wc -l | grep -q '^ *1$' && echo "one ID: the same image"
```

```text
one ID: the same image
```

`docker image inspect` only reads the local image store. The short name and the full name are the same reference; the
digest names the content.

</details>

## Real-world example

A deployment pins its base and runtime images by digest (`FROM python:3.14-slim@sha256:…`), so a rebuild next month
gets exactly the same base even if the `3.14-slim` tag has moved, and a tool such as Renovate or Dependabot opens a pull
request when a new digest is published. CI servers that build many images use a registry mirror or authenticated pulls,
because hundreds of anonymous pulls from one IP address quickly reach Docker Hub's rate limit.

## Recap

- A full image name is `REGISTRY/NAMESPACE/REPOSITORY:TAG`; `docker.io/library/` is the default.
- A pull downloads only missing layers; a tag can move, a digest never does.
- `pull access denied … does not exist or may require 'docker login'`: wrong name, private repository, or no login.
- `429 Too Many Requests`: the registry's rate limit, not a problem with the image.

## Cleanup

<!-- test -->
```bash
docker image rm mirror.gcr.io/library/busybox:1.37 > /dev/null
```

Next: [Lesson 019 · Listing and removing images](../019-listing-and-removing-images/README.md)
