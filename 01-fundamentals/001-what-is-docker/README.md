# Lesson 001 · What is Docker?

> Level 1 · Container fundamentals · ⏱ 15 minutes · run every command from the course folder (`docker-practical-course/`)

## What are we learning?

Docker packages an application **together with everything it needs to run**: the runtime, the libraries, the
dependencies and the configuration. That package (an **image**) runs as a **container**: the same environment on your
laptop, on a colleague's laptop, in CI and on a production server. That is the end of "it works on my machine".

## Visual

```text
 Without containers                                    With Docker

 Developer laptop                                      Application + dependencies + runtime + configuration
   Python 3.14, Flask 3.1, curl 8 …                                     │
   "It works here"                                                      ▼
            │                                                        Image  (built once, versioned)
            ▼                                                           │
 Server                                                   ┌─────────────┼─────────────┐
   Python 3.9, Flask 2.0, no curl …                       ▼             ▼             ▼
   "It doesn't work here"                              laptop          CI          server
                                                     same environment in every place
```

## Lab setup

Docker must be installed and running (lesson 005 explains the installation). The course uses a few official images;
download them once:

<!-- test: contains=hello-world -->
```bash
bash scripts/prefetch-images.sh
```

(If Docker Hub answers `toomanyrequests`, use `bash scripts/prefetch-images.sh --mirror`: troubleshooting problem 25 explains why.)

## Demonstration

Your computer may not have Python 3.14, Node.js 24 and Go 1.26 installed. With Docker it does not matter: each one runs
in a container that brings its own runtime.

<!-- test: contains=Python 3.14; output -->
```bash
docker run --rm python:3.14-slim python --version
docker run --rm node:24-alpine node --version
docker run --rm golang:1.26-alpine go version
```

```text
Python 3.14.8
v24.21.0
go version go1.26.8 linux/amd64
```

Three different runtimes, nothing installed on your computer, and the result is the same on every machine that runs
these images. The containers are removed as soon as they finish (`--rm`).

A container is an isolated process. It sees its own file system, not your computer's:

<!-- test: contains=Alpine Linux; output -->
```bash
docker run --rm alpine:3.23 cat /etc/os-release
```

```text
NAME="Alpine Linux"
ID=alpine
VERSION_ID=3.23.6
PRETTY_NAME="Alpine Linux v3.23"
HOME_URL="https://alpinelinux.org/"
BUG_REPORT_URL="https://gitlab.alpinelinux.org/alpine/aports/-/issues"
```

## Command breakdown

| Command / part | Meaning |
|---|---|
| `docker run IMAGE COMMAND` | create a container from IMAGE and run COMMAND in it |
| `--rm` | remove the container when it stops (lessons 008, 009) |
| `python:3.14-slim` | an image: repository `python`, tag `3.14-slim` (lesson 021) |
| `docker version` | the Docker client and engine versions (lesson 005) |

## Hands-on lab

**Instructions.** Run the PHP 8.5 command-line interpreter from the `php:8.5-fpm-alpine` image and print its version,
without installing PHP.

**Expected result.** A line starting with `PHP 8.5`.

**Verification.**

<!-- test: contains=PHP 8.5 -->
```bash
docker run --rm php:8.5-fpm-alpine php --version
```

## Break it

Ask for a version that does not exist:

<!-- test: fail; anyof=not found||429 Too Many Requests; output -->
```bash
docker run --rm python:3.99-slim python --version 2>&1
```

```text
Unable to find image 'python:3.99-slim' locally
docker: Error response from daemon: unknown: failed to resolve reference "docker.io/library/python:3.99-slim": unexpected status from HEAD request to https://registry-1.docker.io/v2/library/python/manifests/3.99-slim: 429 Too Many Requests

Run 'docker run --help' for more information
```

## Troubleshoot it

Docker could not find the image locally (`Unable to find image … locally`) and asked the registry (Docker Hub) for
the tag `3.99-slim`. The registry answers that it does not exist: `not found` / `manifest unknown`. The container never
started; Python never ran.

You may see `429 Too Many Requests` instead: Docker Hub limits how many requests an anonymous user can make, and
answers every request with 429 until the limit resets. Either way, the message is in the last line and the image was
never downloaded (troubleshooting problem 25 covers pull failures). List
the Python images you do have:

<!-- test: contains=3.14-slim; output -->
```bash
docker image ls python
```

```text
IMAGE                ID             DISK USAGE   CONTENT SIZE   EXTRA
python:3.14-alpine   f6a589d43c42       82.6MB           21MB        
python:3.14-slim     c3e521df8b2b        192MB         48.7MB        
```

## Fix it

Use a tag that exists (the official image's page on Docker Hub lists them):

<!-- test: contains=Python 3.14 -->
```bash
docker run --rm python:3.14-slim python --version
```

## Practice challenge

Show that two containers from the same image are isolated from each other: create a file in one container, then look for
it in a second container started from the same image.

<details>
<summary>Solution</summary>

<!-- test: contains=No such file; output -->
```bash
docker run --rm alpine:3.23 sh -c 'echo hello > /tmp/note.txt && cat /tmp/note.txt'
docker run --rm alpine:3.23 cat /tmp/note.txt 2>&1 || true
```

```text
hello
cat: can't open '/tmp/note.txt': No such file or directory
```

The second container starts from the image again, not from the first container: the file does not exist there.

</details>

## Real-world example

A team's API needs Python 3.14, a specific `libpq` and a CA certificate bundle. Without containers, every developer and
every server installs them by hand and they drift apart. With Docker, the team builds one image in CI, tests it, and
deploys exactly that image to staging and production: if it passed the tests, the same bytes run in production.

## Recap

- Docker packages an application with its runtime, dependencies and configuration into an image.
- A container is a running instance of an image: an isolated process with its own file system.
- The same image behaves the same on every machine: no more "it works on my machine".

## Cleanup

Nothing to clean: `--rm` removed every container.

Next: [Lesson 002 · Why containers?](../002-why-containers/README.md)
