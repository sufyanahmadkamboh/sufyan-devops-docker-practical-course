# Lesson 021 · The danger of the latest tag

> Level 4 · Images · ⏱ 15 minutes · run every command from the course folder

## What are we learning?

`latest` is not magic and not "the newest version". It is an ordinary tag that Docker uses **when you do not write
one**: `docker run nginx` means `nginx:latest`, `docker build -t cafe-menu .` creates `cafe-menu:latest`. Whatever was
tagged `latest` most recently (or pushed most recently) wins, so the same command can run different software on
different days and machines. Production uses explicit versions.

## Visual

```text
  Monday     docker build -t cafe-menu .        cafe-menu:latest ──▶ v1     server A runs v1
  Tuesday    docker build -t cafe-menu .        cafe-menu:latest ──▶ v2     server B pulls: v2
  Wednesday  hotfix built from an old branch    cafe-menu:latest ──▶ v1-fix server C pulls: v1-fix

             same command "docker run cafe-menu" → three different programs, and no record of which one

  instead:   cafe-menu:1.4.3   (exact, never moves)    or    cafe-menu@sha256:…  (content, can never change)
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-021
cd ~/docker-practice/lesson-021
printf 'FROM alpine:3.23\nARG VERSION\nRUN echo "cafe menu $VERSION" > /version\nCMD ["sleep", "3600"]\n' > Dockerfile
```

## Demonstration

Without a tag, Docker uses `latest`:

<!-- test: contains=cafe-menu:latest; output -->
```bash
docker build -q --build-arg VERSION=1.0 -t cafe-menu . > /dev/null
docker image ls --format '{{.Repository}}:{{.Tag}}' cafe-menu
```

```text
cafe-menu:latest
```

`latest` is only a name. You have two Nginx images, yet `nginx` alone does not refer to either of them:

<!-- test: contains=No such image; output -->
```bash
docker image ls --format '{{.Repository}}:{{.Tag}}' nginx
docker image inspect nginx > /dev/null 2>&1 || echo "Error: No such image: nginx (= nginx:latest)"
```

```text
nginx:1.30-alpine
nginx:1.29-alpine
Error: No such image: nginx (= nginx:latest)
```

`docker run nginx` would therefore download `nginx:latest` from Docker Hub: whatever version that tag points to today,
on a different base (Debian instead of Alpine) than the images you tested.

## Command breakdown

| Command | Means |
|---|---|
| `docker run nginx` | `docker run docker.io/library/nginx:latest` |
| `docker build -t cafe-menu .` | `docker build -t cafe-menu:latest .` |
| `FROM python` in a Dockerfile | `FROM python:latest`: a different base every few months |
| `docker container inspect --format '{{.Image}}' NAME` | the image **ID** a container really runs |

## Hands-on lab

**Instructions.** Start a container `menu-a` from `cafe-menu` (no tag), then print the image ID it uses and the
version file inside it.

**Expected result.** An image ID (`sha256:…`) and `cafe menu 1.0`.

**Verification.**

<!-- test: contains=cafe menu 1.0 -->
```bash
cd ~/docker-practice/lesson-021
docker run -d --name menu-a cafe-menu > /dev/null
docker container inspect --format '{{.Image}}' menu-a
docker exec menu-a cat /version
```

## Break it

A colleague builds a new version, also without a tag, and a second container is started "the same way":

<!-- test: contains=cafe menu 2.0; contains=cafe menu 1.0; output -->
```bash
docker build -q --build-arg VERSION=2.0 -t cafe-menu . > /dev/null
docker run -d --name menu-b cafe-menu > /dev/null
echo "menu-a: $(docker exec menu-a cat /version)"
echo "menu-b: $(docker exec menu-b cat /version)"
```

```text
menu-a: cafe menu 1.0
menu-b: cafe menu 2.0
```

Two containers, both started with `docker run cafe-menu`, run different software. If `menu-b` has a bug, which code is
it, and what do you roll back to? "latest" does not say.

## Troubleshoot it

Compare the image each container was started *by name* with the image *ID* it really runs:

<!-- test: contains=menu-a; contains=menu-b; output -->
```bash
docker container ls --format '{{.Names}}  name={{.Image}}' --filter name=menu-
for c in menu-a menu-b; do echo "$c runs $(docker container inspect --format '{{.Image}}' $c | cut -c1-19)"; done
echo "cafe-menu:latest is now $(docker image inspect --format '{{.Id}}' cafe-menu:latest | cut -c1-19)"
```

```text
menu-b  name=cafe-menu
menu-a  name=7448c93a9a88
menu-a runs sha256:7448c93a9a88
menu-b runs sha256:b1ed18ebfcf3
cafe-menu:latest is now sha256:b1ed18ebfcf3
```

`menu-a` was started from `cafe-menu`, but `latest` has moved since: the old image lost its name and Docker can only
show its ID. The tag tells you nothing reliable about what is running; only the image ID or digest does.

## Fix it

Give every build an explicit version tag, and deploy that tag:

<!-- test: contains=menu-v2: cafe menu 2.0 -->
```bash
docker build -q --build-arg VERSION=2.0 -t cafe-menu:2.0 . > /dev/null
docker run -d --name menu-v2 cafe-menu:2.0 > /dev/null
echo "menu-v2: $(docker exec menu-v2 cat /version)"
```

`docker run cafe-menu:2.0` runs 2.0 today, tomorrow and on every server. Pin base images the same way (`FROM
alpine:3.23`, never `FROM alpine`), or by digest for complete reproducibility (lesson 018).

## Practice challenge

Your Dockerfile starts with `FROM python`. Without pulling anything, find out which of your local Python images that
line would *not* use, and rewrite the line so that it uses the slim 3.14 image you tested.

<details>
<summary>Solution</summary>

<!-- test: contains=FROM python:3.14-slim; output -->
```bash
docker image ls --format '{{.Repository}}:{{.Tag}}' python
docker image inspect python:latest > /dev/null 2>&1 || echo "python:latest is not local: FROM python would pull it"
echo "FROM python" | sed 's/^FROM python$/FROM python:3.14-slim/'
```

```text
python:3.14-slim
python:3.14-alpine
python:latest is not local: FROM python would pull it
FROM python:3.14-slim
```

`FROM python` means `python:latest`: neither local image. It would pull whatever `latest` is today (a full Debian image
with the newest Python), so the next build silently changes Python version and image size.

</details>

## Real-world example

A Kubernetes deployment uses `image: cafe-menu:latest`. A node that already has an old `latest` keeps running it, a new
node pulls the new one: the same deployment runs two versions at once, and rolling back to "the previous latest" is
impossible because nobody recorded it. The usual fixes: CI tags images with the version or commit, deployments
reference exact tags or digests, and some registries are configured to make tags immutable so a pushed version can
never be overwritten.

## Recap

- `latest` is the default tag when none is given, not "the newest".
- It moves with every untagged build or push, so it does not identify what runs.
- Image IDs and digests identify content; exact version tags identify releases.
- Pin base images and deployments to explicit versions.

## Cleanup

<!-- test -->
```bash
docker rm -f menu-a menu-b menu-v2 > /dev/null
docker image rm -f cafe-menu:latest cafe-menu:2.0 > /dev/null
docker image prune -f > /dev/null
rm -rf ~/docker-practice/lesson-021
```

Next: [Lesson 022 · Your first Dockerfile](../../04-dockerfiles/022-first-dockerfile/README.md)
