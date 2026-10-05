# Lesson 004 · Docker architecture

> Level 1 · Container fundamentals · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

`docker` is only a **client**. Every command you type becomes an HTTP request to the **Docker daemon** (`dockerd`, the
engine), which does the real work: it pulls **images** from a **registry**, stores them, and asks **containerd** and
**runc** to create and run **containers**. Knowing which part does what tells you where to look when something fails.

## Visual

```text
  Your terminal                       Docker host (on Docker Desktop: a small Linux VM)
 ┌──────────────┐   REST API over    ┌──────────────────────────────────────────────────────┐
 │ docker CLI   │ ─ a socket/pipe ─▶ │ dockerd (Docker Engine)                              │
 │ (client)     │ ◀───────────────── │   images · networks · volumes · build · API          │
 └──────────────┘                    │        │                                             │
                                     │        ▼                                             │
                                     │ containerd  (container lifecycle, image storage)     │
                                     │        │                                             │
                                     │        ▼                                             │
                                     │ runc  (creates the isolated process: namespaces,     │
                                     │        cgroups) ──▶ container  container  container  │
                                     └────────┬─────────────────────────────────────────────┘
                                              │ pull / push
                                              ▼
                                     ┌──────────────────────┐
                                     │ Registry             │  Docker Hub, GHCR, ECR, a private
                                     │ (stores images)      │  registry (lessons 075–079)
                                     └──────────────────────┘
```

| Component | Role |
|---|---|
| Docker client (`docker`) | turns commands into API requests; holds no containers itself |
| Docker daemon (`dockerd`) | the engine: manages images, containers, networks, volumes, builds |
| containerd | runs and supervises containers for the daemon (also used directly by Kubernetes) |
| runc | the low-level runtime that creates the isolated process, then exits |
| Image | a read-only template: files + metadata (lesson 007) |
| Container | a running (or stopped) instance of an image |
| Registry | a server that stores and distributes images |

## Lab setup

No files are needed: this lesson asks the engine about itself.

## Demonstration

The client and the server are two separate programs, each with its own version:

<!-- test: contains=-> server; output -->
```bash
docker version --format 'client {{.Client.Version}} (API {{.Client.APIVersion}}) -> server {{.Server.Version}} (API {{.Server.APIVersion}})'
```

```text
client 29.4.3 (API 1.54) -> server 29.4.3 (API 1.54)
```

The server reports the components behind it:

<!-- test: contains=runc; output -->
```bash
docker version --format '{{range .Server.Components}}{{.Name}} {{.Version}}{{"\n"}}{{end}}'
```

```text
Engine 29.4.3
containerd v2.2.3
runc 1.3.5
docker-init 0.19.0
```

`docker run` is several steps in one. Do them one by one: **create** the container from the image (the engine pulls
the image first if it is missing), then **start** it:

<!-- test: contains=Exited (0); output -->
```bash
docker container create --name demo alpine:3.23 echo "hello from the container" > /dev/null
docker container ls -a --filter name=demo --format '{{.Names}}: {{.Status}}'
docker container start -a demo
docker container ls -a --filter name=demo --format '{{.Names}}: {{.Status}}'
docker container rm demo > /dev/null
```

```text
demo: Created
hello from the container
demo: Exited (0) Less than a second ago
```

The client only sent requests; the daemon stored the container, containerd and runc ran it, and the container stayed on
the host after it exited until `rm` removed it.

## Command breakdown

| Command | What it does |
|---|---|
| `docker version` | versions of the client and of the server components |
| `--format '{{…}}'` | print only chosen fields (a Go template; used throughout the course) |
| `docker container create` | the daemon creates a container from an image, without starting it |
| `docker container start -a` | start it and attach to its output |
| `docker context ls` | the engines this client knows about, and which one is active |

## Hands-on lab

**Instructions.** Find which engine endpoint your client talks to, with `docker context ls` (the active context has a
`*`) and `docker context show`.

**Expected result.** One context marked active; its `DOCKER ENDPOINT` is a Unix socket (`unix:///var/run/docker.sock`)
on Linux or a named pipe (`npipe:////./pipe/…`) on Windows.

**Verification.**

<!-- test: anyof=unix://||npipe:// -->
```bash
docker context ls
docker context show
```

## Break it

Point the client at an address where no daemon is listening (`DOCKER_HOST` overrides the context):

<!-- test: fail; anyof=error during connect||Cannot connect to the Docker daemon; output -->
```bash
DOCKER_HOST=tcp://127.0.0.1:1 docker version --format '{{.Server.Version}}' 2>&1
```

```text

error during connect: Get "http://127.0.0.1:1/v1.54/version": dial tcp 127.0.0.1:1: connectex: No connection could be made because the target machine actively refused it.
```

## Troubleshoot it

The client works (it printed an error, it did not crash) but it cannot reach any daemon. The message names the address
it tried: `127.0.0.1:1`. On Linux the same mistake reads `Cannot connect to the Docker daemon at …` or
`connection refused`. Every "cannot connect" error has one of three causes:

1. the daemon is not running (Docker Desktop stopped, `systemctl status docker` on Linux),
2. the client points to the wrong place (`DOCKER_HOST`, or the wrong context),
3. you may not use the socket (on Linux: not in the `docker` group, so `permission denied`).

Check where the client is pointing:

<!-- test: contains=context -->
```bash
echo "DOCKER_HOST=${DOCKER_HOST:-(not set)}"
echo "context: $(docker context show)"
```

## Fix it

Remove the override (in a real shell: `unset DOCKER_HOST`, and remove it from your shell profile if it is set there), so
the client uses its active context again:

<!-- test: contains=server is reachable -->
```bash
unset DOCKER_HOST
docker version --format '{{.Server.Version}}' > /dev/null && echo "server is reachable"
```

## Practice challenge

`docker run` = pull (if needed) + create + start. Using only `docker image pull`, `docker container create` and
`docker container start -a`, run `busybox:1.37` with the command `echo it works`, then remove the container.

<details>
<summary>Solution</summary>

<!-- test: contains=it works; output -->
```bash
docker image inspect busybox:1.37 > /dev/null 2>&1 || docker image pull -q busybox:1.37
docker container create --name by-hand busybox:1.37 echo it works > /dev/null
docker container start -a by-hand
docker container rm by-hand > /dev/null
```

```text
it works
```

Each command is one request to the daemon. `docker run` sends the same requests for you, and like the first line it
only pulls when the image is missing: an explicit `docker image pull` always asks the registry for the latest digest.

</details>

## Real-world example

A CI runner builds images by talking to a Docker daemon on another machine, or to a BuildKit service. A deployment tool
on a laptop manages a remote server with `docker context create prod --docker host=ssh://deploy@server`. Kubernetes
skips `dockerd` entirely and talks to containerd directly: the images you build with Docker run there unchanged,
because they follow the same open (OCI) image format.

## Recap

- The `docker` CLI is a client; `dockerd` is the engine that does the work, through containerd and runc.
- Client and daemon talk over a REST API on a socket or named pipe; a context says which daemon to use.
- "Cannot connect to the Docker daemon": daemon not running, wrong `DOCKER_HOST`/context, or no permission.
- Registries store images; the daemon pulls from and pushes to them.

## Cleanup

Nothing to clean: every container was removed.

Next: [Lesson 005 · Installing Docker](../005-installing-docker/README.md)
