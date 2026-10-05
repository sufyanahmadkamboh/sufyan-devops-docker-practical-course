# Lesson 019 · Listing and removing images

> Level 4 · Images · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

Images pile up: every pull and every build leaves one behind. This lesson lists them (`docker image ls`, with filters
and formats), removes them safely (`docker image rm`), and cleans up **dangling** images: images that no longer have a
name, typically left behind by builds.

## Visual

```text
  docker image ls                                  what removing does

  name (tag)          image ID                     docker image rm cafe:1.1
  cafe:1.1  ───────┐                                 ├─ another tag points to the same ID?  → "Untagged" only
  cafe:latest ─────┴─▶ 4e91ae7992f1                  ├─ a container (even stopped) uses it? → refused: conflict
  cafe:1.0  ─────────▶ 60c13e724dd4                  └─ otherwise                           → "Untagged" + "Deleted"
  <none>:<none> ─────▶ 9707e1f15475  ← dangling:
                                       no name left  docker image prune      removes dangling images only
                                                     docker image prune -a   removes EVERY image no container uses
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-019 examples/site
cd ~/docker-practice/lesson-019
printf 'FROM nginx:1.30-alpine\nCOPY . /usr/share/nginx/html/\n' > Dockerfile
ls
```

The cafe's static website and a two-line Dockerfile that serves it with Nginx (Dockerfiles start in lesson 022).

## Demonstration

Build the site twice, as two versions, and list the result:

<!-- test: contains=cafe-site; contains=1.1; output -->
```bash
docker build -q -t cafe-site:1.0 . > /dev/null
echo "<p>New: oat milk.</p>" >> index.html
docker build -q -t cafe-site:1.1 . > /dev/null
docker image ls --format 'table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}' cafe-site
```

```text
REPOSITORY   TAG       IMAGE ID       SIZE
cafe-site    1.1       6a22e6401e50   92.8MB
cafe-site    1.0       4c70856ffdef   92.8MB
```

Useful ways to narrow the list down:

<!-- test: contains=python:3.14-slim -->
```bash
docker image ls --filter reference='python'                    # one repository
docker image ls --filter reference='*:*-alpine' --format '{{.Repository}}:{{.Tag}}'   # a name pattern
docker image ls --filter before=cafe-site:1.1 --format '{{.Repository}}:{{.Tag}}' cafe-site
docker image ls -q cafe-site                                   # only IDs, for scripts
```

A build without `-t` produces an image with no name: a **dangling** image.

<!-- test: contains=<none>; output -->
```bash
echo "<p>Draft: new opening hours.</p>" >> index.html
docker build -q . > /dev/null
docker image ls --filter dangling=true --format '{{.Repository}}:{{.Tag}}  {{.ID}}'
```

```text
<none>:<none>  c4c3005d43c1
```

Dangling images also appear when you rebuild a tag: the tag moves to the new image and the old one loses its name (with
Docker's classic image store it is listed as `<none>`; the containerd image store, the default of Docker Desktop and
new Docker Engine 29 installations, removes the old one when nothing else uses it). Remove all dangling images:

<!-- test: contains=reclaimed space -->
```bash
docker image prune -f
```

## Command breakdown

| Command | What it does |
|---|---|
| `docker image ls` (`docker images`) | list images; `-a` also shows intermediate images |
| `--filter reference=PATTERN` | only names matching a pattern (`*` wildcard) |
| `--filter dangling=true` | only images without a name |
| `--filter before=IMAGE` / `since=IMAGE` | images created before / after another one |
| `--format 'table {{.Repository}}\t{{.Tag}}'` | choose the columns |
| `-q` | IDs only |
| `docker image rm NAME:TAG` (`docker rmi`) | remove a name, and the image when no other name refers to it |
| `docker image prune [-f]` | remove dangling images (`-f`: without asking) |
| `docker image prune -a` | remove every image not used by a container: **all** your cached images |

## Hands-on lab

**Instructions.** Remove `cafe-site:1.0` and verify that `cafe-site:1.1` is still there.

**Expected result.** `Untagged: cafe-site:1.0` and `Deleted: sha256:…`; the list shows only version 1.1.

**Verification.**

<!-- test: contains=Untagged: cafe-site:1.0; contains=cafe-site:1.1 -->
```bash
docker image rm cafe-site:1.0
docker image ls --format '{{.Repository}}:{{.Tag}}' cafe-site
```

## Break it

Start a container from `cafe-site:1.1`, stop it, and then try to remove the image:

<!-- test: fail; contains=conflict; output -->
```bash
docker run -d --name cafe-site cafe-site:1.1 > /dev/null
docker stop cafe-site > /dev/null
docker image rm cafe-site:1.1
```

```text
Error response from daemon: conflict: unable to delete cafe-site:1.1 (must be forced) - container b16c0e650cea is using its referenced image 6a22e6401e50
```

## Troubleshoot it

`conflict: unable to delete … container 3c9d1b2f8a4e is using its referenced image`: a container needs its image's
layers, even when it is **stopped** (it can be started again). Docker refuses to delete them. Find the containers that
use the image, running or not:

<!-- test: contains=cafe-site; output -->
```bash
docker container ls -a --filter ancestor=cafe-site:1.1 --format '{{.Names}}  {{.Status}}'
```

```text
cafe-site  Exited (0) Less than a second ago
```

## Fix it

Remove the container first (if you no longer need it), then the image:

<!-- test: contains=Deleted -->
```bash
docker rm cafe-site
docker image rm cafe-site:1.1
```

`docker image rm -f` would remove the *name* anyway, but the stopped container keeps the image's data on disk as an
unnamed image: `-f` hides the problem instead of solving it.

## Practice challenge

Create two tags for the same image (`docker image tag alpine:3.23 cafe-base:1` and `cafe-base:1.0`), remove one, then
the other. Explain why the first removal prints only `Untagged` and why `alpine:3.23` survives both.

<details>
<summary>Solution</summary>

<!-- test: contains=Untagged: cafe-base:1.0; contains=alpine:3.23; output -->
```bash
docker image tag alpine:3.23 cafe-base:1
docker image tag alpine:3.23 cafe-base:1.0
docker image rm cafe-base:1
docker image rm cafe-base:1.0
docker image ls --format '{{.Repository}}:{{.Tag}}' alpine
```

```text
Untagged: cafe-base:1
Untagged: cafe-base:1.0
alpine:3.23
```

A tag is only a name pointing to an image ID (lesson 020). `docker image rm` removes the name; the image itself is
deleted only when no name and no container refers to it any more. Here `alpine:3.23` still points to it, so both
removals only untag.

</details>

## Real-world example

A CI server builds dozens of images a day and runs out of disk within weeks. The team schedules
`docker image prune -f` (dangling images) daily and `docker image prune -a -f --filter until=168h` (anything unused for a
week) weekly, and checks the space with `docker system df`. On a developer laptop, `docker image prune -a` is the
"reclaim everything" button, with the cost that every image must be downloaded again.

## Recap

- `docker image ls` with `--filter` and `--format` finds exactly the images you need.
- `docker image rm` removes a name; the image is deleted when nothing else refers to it.
- A container, even a stopped one, blocks the removal of its image: remove the container first.
- Dangling images have no name; `docker image prune` removes them, `prune -a` removes everything unused.

## Cleanup

<!-- test -->
```bash
docker image prune -f > /dev/null
rm -rf ~/docker-practice/lesson-019
```

Next: [Lesson 020 · Image tags](../020-image-tags/README.md)
