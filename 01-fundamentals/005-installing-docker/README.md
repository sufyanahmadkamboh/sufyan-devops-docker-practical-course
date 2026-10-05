# Lesson 005 · Installing Docker

> Level 1 · Container fundamentals · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

How to install Docker on each operating system, and how to **verify** an installation instead of assuming it works:
`docker version` (are the client and the engine both there?), `docker info` (how is the engine configured?) and
`docker run hello-world` (can it pull and run a container end to end?).

## Visual

```text
 Windows / macOS                                 Linux
 ┌───────────────────────────────────┐           ┌───────────────────────────────────┐
 │ Docker Desktop                    │           │ Docker Engine (packages)          │
 │  docker CLI + Compose + Buildx    │           │  docker-ce  docker-ce-cli         │
 │        │                          │           │  containerd.io                    │
 │        ▼                          │           │  docker-buildx-plugin             │
 │  small Linux VM (WSL 2 / Apple    │           │  docker-compose-plugin            │
 │  virtualization) runs dockerd     │           │  dockerd runs directly on the host│
 └───────────────────────────────────┘           └───────────────────────────────────┘
                 \                                              /
                  └────────── verify: docker version ──────────┘
                                docker info
                                docker run hello-world
```

## Lab setup

Install Docker once, following the section for your operating system. Every later lesson assumes it is running.

**Windows 10/11 and macOS:** install **Docker Desktop** from <https://docs.docker.com/get-started/get-docker/>. On
Windows, choose the WSL 2 backend. Start Docker Desktop and wait until it reports that the engine is running.

**Linux (Ubuntu, Debian, Fedora, …):** install **Docker Engine** from Docker's own package repository, as described for
your distribution at <https://docs.docker.com/engine/install/>. On Ubuntu, after adding the repository:

<!-- test: skip -->
```bash
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"     # use docker without sudo; log out and in again
```

> Membership of the `docker` group is equivalent to root access on that machine (lesson 080 explains why). On a shared
> server, give it only to people who are allowed to be root.

## Demonstration

**1. Client and engine.** Both sections must be present: `Client` alone means the engine is not running.

<!-- test: contains=Server; output -->
```bash
docker version --format 'Client: {{.Client.Version}} {{.Client.Os}}/{{.Client.Arch}}{{"\n"}}Server: {{.Server.Version}} {{.Server.Os}}/{{.Server.Arch}}'
```

```text
Client: 29.4.3 windows/amd64
Server: 29.4.3 linux/amd64
```

On Windows the client is a Windows program and the server is Linux: the engine runs in Docker Desktop's Linux VM.

**2. Engine configuration.** `docker info` prints a long report; `--format` picks out the fields you need:

<!-- test: contains=storage driver; output -->
```bash
docker info --format 'engine {{.ServerVersion}} on {{.OperatingSystem}} ({{.OSType}}/{{.Architecture}})
CPUs: {{.NCPU}}, memory: {{.MemTotal}} bytes
storage driver: {{.Driver}}, data in {{.DockerRootDir}}
containers: {{.Containers}}, images: {{.Images}}'
```

```text
engine 29.4.3 on Docker Desktop (linux/x86_64)
CPUs: 14, memory: 16486322176 bytes
storage driver: overlayfs, data in /var/lib/docker
containers: 0, images: 20
```

The CPUs and memory are what containers can use in total. On Docker Desktop they are the VM's limits, set in Docker
Desktop's settings, not your whole computer.

**3. End to end.** `hello-world` checks everything at once: the client reaches the daemon, the image is available, and
a container runs:

<!-- test: contains=Hello from Docker!; output -->
```bash
docker run --rm hello-world | head -3
```

```text

Hello from Docker!
This message shows that your installation appears to be working correctly.
```

## Command breakdown

| Command | What it checks |
|---|---|
| `docker version` | client and server versions; a missing `Server` section means no engine |
| `docker info` | engine configuration: storage driver, CPUs, memory, counts, warnings |
| `docker info --format '{{.Field}}'` | one field of that report (names are case-sensitive) |
| `docker info --format '{{json .}}'` | the whole report as JSON, to discover field names |
| `docker run hello-world` | the full path: client → daemon → image → container |

## Hands-on lab

**Instructions.** Print, on one line, the engine version, the storage driver and the logging driver of your engine.

**Expected result.** Three values, for example `29.4.3 overlayfs json-file` (versions and the storage driver differ
between installations).

**Verification.**

<!-- test: contains=json-file -->
```bash
docker info --format '{{.ServerVersion}} {{.Driver}} {{.LoggingDriver}}'
```

## Break it

A typo in a field name:

<!-- test: fail; contains=can't evaluate field; output -->
```bash
docker info --format '{{.ServerVersoin}}'
```

```text

template: :1:2: executing "" at <.ServerVersoin>: can't evaluate field ServerVersoin in type system.dockerInfo
```

## Troubleshoot it

`can't evaluate field ServerVersoin`: the template is valid, but `docker info` has no field of that name. Field names
are case-sensitive and spelled exactly as in the JSON form of the report. List the fields that start with `Server`:

<!-- test: contains=ServerVersion; output -->
```bash
docker info --format '{{json .}}' | grep -o '"Server[A-Za-z]*"' | sort -u
```

```text
"ServerVersion"
```

## Fix it

<!-- test: contains=29 -->
```bash
docker info --format '{{.ServerVersion}}'
```

Other installation problems and their fixes:

| Symptom | Cause | Fix |
|---|---|---|
| `Cannot connect to the Docker daemon` | engine not running | start Docker Desktop / `sudo systemctl start docker` |
| `permission denied … docker.sock` | Linux user not in the `docker` group | `sudo usermod -aG docker "$USER"`, then log in again |
| `docker: command not found` | CLI not installed or not on `PATH` | reinstall; open a new terminal |
| `WSL 2 installation is incomplete` | Windows feature missing | `wsl --install` in an administrator PowerShell, reboot |

## Practice challenge

Write a one-line health report of your installation: the client version, the server version, the number of running
containers and the number of images. Use only `--format` (no `grep`).

<details>
<summary>Solution</summary>

<!-- test: contains=images; output -->
```bash
echo "client $(docker version --format '{{.Client.Version}}'), server $(docker info --format '{{.ServerVersion}}'), $(docker info --format '{{.ContainersRunning}} running, {{.Images}} images')"
```

```text
client 29.4.3, server 29.4.3, 0 running, 20 images
```

`docker version` knows the client; `docker info` describes the engine.

</details>

## Real-world example

A team's onboarding script ends with a check like the challenge: it fails fast with a clear message when the engine is
not running or is too old (`docker version --format '{{.Server.Version}}'` compared with the minimum version), instead
of letting a new developer discover it through a confusing build error an hour later. CI pipelines print
`docker version` and `docker info` at the start of a job for the same reason: when a build fails, the log shows exactly
which engine ran it.

## Recap

- Windows and macOS: Docker Desktop (the engine runs in a small Linux VM). Linux: Docker Engine from Docker's repository.
- Verify with `docker version` (client and server), `docker info` (configuration) and `docker run hello-world`.
- `--format` with Go templates extracts single fields; field names are case-sensitive.
- The `docker` group grants root-equivalent access on Linux.

## Cleanup

Nothing to clean: `--rm` removed the container.

Next: [Lesson 006 · Your first container](../../02-containers/006-first-container/README.md)
