# Lesson 006 · Your first container

> Level 2 · First container · ⏱ 15 minutes · run every command from the course folder

## What are we learning?

`docker run hello-world` is the smallest complete container run. It looks like one command, but Docker does four
things: it looks for the image locally, downloads it from a registry if it is missing, creates a container from it, and
starts it. The container prints a message and exits. Understanding these steps is what lets you read every later error.

## Visual

```text
 docker run hello-world
        │
        ▼
 1. Is the image hello-world:latest on this machine? ── no ──▶ 2. pull it from the registry (Docker Hub)
        │ yes                                                              │
        ▼◀─────────────────────────────────────────────────────────────────┘
 3. create a container from the image   (new ID, a random name, a writable layer)
        │
        ▼
 4. start it: run the image's command (/hello) → prints the message → the process ends
        │
        ▼
 the container is now "Exited (0)": stopped, but still there until you remove it
```

## Lab setup

No files are needed: this lesson runs containers from the pinned images (`bash scripts/prefetch-images.sh` from lesson
001 downloaded them).

## Demonstration

Run it:

<!-- test: contains=Hello from Docker!; output -->
```bash
docker run hello-world
```

```text

Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (amd64)
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
 https://hub.docker.com/

For more examples and ideas, visit:
 https://docs.docker.com/get-started/
```

Read the message: it lists the same four steps as the diagram. When the image is not on your machine yet, Docker first
prints `Unable to find image 'hello-world:latest' locally` and the download progress.

The container did its job and exited. It is not running any more, so `docker ps` (running containers) does not show
it, but `docker ps -a` (all containers) does:

<!-- test: contains=hello-world; contains=Exited (0); output -->
```bash
docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
```

```text
NAMES              IMAGE         STATUS
confident_wilson   hello-world   Exited (0) Less than a second ago
```

Docker gave it a random name made of an adjective and a scientist's name, because we did not choose one (lesson 010).
Add `--rm` and Docker removes the container as soon as it exits:

<!-- test: contains=hello-world containers: 1; output -->
```bash
docker run --rm hello-world > /dev/null
echo "hello-world containers: $(docker ps -aq --filter ancestor=hello-world | wc -l | tr -d ' ')"
```

```text
hello-world containers: 1
```

Still one container: the one from the first run. The `--rm` run left nothing behind.

## Command breakdown

| Command / part | Meaning |
|---|---|
| `docker run IMAGE` | pull (if missing) + create + start a container from IMAGE |
| `hello-world` | short for `docker.io/library/hello-world:latest` (lesson 077) |
| `--rm` | remove the container when it exits |
| `docker ps` | running containers only |
| `docker ps -a` | all containers, including stopped ones (lesson 008) |
| `--filter ancestor=IMAGE` | only containers created from IMAGE |

## Hands-on lab

**Instructions.** Run `busybox:1.37` with the command `echo "my first container"`, so that the container is removed
automatically when it exits. Then check that no `busybox` container is left.

**Expected result.** The text `my first container`, and `0` containers left from that image.

**Verification.**

<!-- test: contains=my first container; contains=busybox containers: 0 -->
```bash
docker run --rm busybox:1.37 echo "my first container"
echo "busybox containers: $(docker ps -aq --filter ancestor=busybox:1.37 | wc -l | tr -d ' ')"
```

## Break it

A typo in the image name:

<!-- test: fail; anyof=pull access denied||429 Too Many Requests; output -->
```bash
docker run hello-word 2>&1
```

```text
Unable to find image 'hello-word:latest' locally
docker: Error response from daemon: pull access denied for hello-word, repository does not exist or may require 'docker login'

Run 'docker run --help' for more information
```

## Troubleshoot it

Read the steps again. Step 1 failed silently (no local image `hello-word`), so Docker went to step 2 and asked Docker
Hub for the repository `library/hello-word`. The answer:

- `pull access denied for hello-word, repository does not exist or may require 'docker login'`: there is no public
  repository of that name. Docker cannot tell "does not exist" from "private", so it mentions `docker login`; that is
  misleading here, the name is simply wrong.
- `429 Too Many Requests`: Docker Hub refused because of its rate limit, before even checking the name
  (troubleshooting problem 25).

Either way no container was created. Compare with the images you actually have:

<!-- test: contains=hello-world -->
```bash
docker image ls --format '{{.Repository}}:{{.Tag}}' | grep hello
```

## Fix it

Use the correct name:

<!-- test: contains=Hello from Docker! -->
```bash
docker run --rm hello-world | grep "Hello from Docker"
```

## Practice challenge

Run `hello-world` twice **without** `--rm`, count how many `hello-world` containers exist, then remove exactly those
containers with one command.

<details>
<summary>Solution</summary>

<!-- test: contains=removed; output -->
```bash
docker run hello-world > /dev/null
docker run hello-world > /dev/null
echo "hello-world containers: $(docker ps -aq --filter ancestor=hello-world | wc -l | tr -d ' ')"
docker rm $(docker ps -aq --filter ancestor=hello-world) > /dev/null && echo "removed"
echo "hello-world containers: $(docker ps -aq --filter ancestor=hello-world | wc -l | tr -d ' ')"
```

```text
hello-world containers: 3
removed
hello-world containers: 0
```

Three, not two: the container from the Demonstration is still there. Every `docker run` without `--rm` creates a new
container; stopped containers pile up until you remove them. `-q` prints only IDs, which is what `docker rm` expects.

</details>

## Real-world example

CI jobs and scripts run short-lived tools in containers: a linter, a database migration, a test suite. They use
`docker run --rm` so that hundreds of runs per day leave no stopped containers behind. On a developer laptop, a forgotten
`--rm` is why `docker ps -a` eventually lists dozens of exited containers using disk space.

## Recap

- `docker run` = find or pull the image, create a container, start it.
- A container whose process ends is **exited**, not deleted: `docker ps -a` still lists it.
- `--rm` removes the container automatically when it exits.
- `pull access denied … repository does not exist` usually means a typo in the image name.

## Cleanup

<!-- test -->
```bash
docker rm -f $(docker ps -aq --filter ancestor=hello-world) > /dev/null 2>&1 || true
```

Next: [Lesson 007 · Images vs containers](../007-images-vs-containers/README.md)
