# Module 01 assessment · Container fundamentals

> Lessons [001](001-what-is-docker/README.md)–[005](005-installing-docker/README.md) · ⏱ 30 minutes · try every
> question before opening its answer

## Knowledge check

**1. What does a Docker image contain that a plain copy of your source code does not?**

<details><summary>Answer</summary>

The runtime, the libraries and system dependencies in exact versions, and default configuration: everything the
application needs to run, packaged together (lessons 001, 002).

</details>

**2. What is the difference between an image and a container?**

<details><summary>Answer</summary>

An image is a read-only template; a container is an instance of it, a process with its own writable layer. One image
can run as many containers (lesson 001, in depth in lesson 007).

</details>

**3. Why does a container start in under a second while a VM takes much longer?**

<details><summary>Answer</summary>

A container is an isolated process on the host's kernel: nothing boots. A VM boots a whole guest operating system with
its own kernel (lesson 003).

</details>

**4. Two containers run Alpine and Debian on the same host. Which kernel does each one use?**

<details><summary>Answer</summary>

The same one: the host's (on Docker Desktop, the Linux VM's). Containers share the kernel (lesson 003).

</details>

**5. Name the components between `docker run` and the running process.**

<details><summary>Answer</summary>

The `docker` client sends an API request to the daemon `dockerd`, which uses containerd, which uses runc to create the
isolated process (lesson 004).

</details>

**6. `docker version` prints a `Client` section but no `Server` section. What does that tell you?**

<details><summary>Answer</summary>

The CLI is installed but cannot reach an engine: the daemon is not running, or the client points to the wrong place
(`DOCKER_HOST`, the context) (lessons 004, 005).

</details>

**7. Why is membership of the `docker` group on Linux a security decision?**

<details><summary>Answer</summary>

Whoever can use the Docker socket can start a privileged container that mounts the host's file system: it is
equivalent to root access (lesson 005, in depth in lesson 080).

</details>

**8. When should you choose a VM instead of a container?**

<details><summary>Answer</summary>

When the workload needs its own kernel (a different OS, kernel modules, kernel settings that are not namespaced) or
strong isolation between untrusted tenants (lesson 003).

</details>

## Practical task

Without installing anything, print the Node.js version of the `node:24-alpine` image, the kernel release a container
of that image sees, and whether that kernel is the engine's kernel.

<details><summary>Solution</summary>

<!-- test: contains=engine kernel: yes; output -->
```bash
docker run --rm node:24-alpine node --version
kernel=$(docker run --rm node:24-alpine uname -r)
echo "kernel: $kernel"
[ "$kernel" = "$(docker info --format '{{.KernelVersion}}')" ] && echo "engine kernel: yes"
```

```text
v24.21.0
kernel: 6.6.114.1-microsoft-standard-WSL2
engine kernel: yes
```

</details>

## Troubleshooting task

A colleague's terminal fails on every Docker command. Reproduce their setup:

<!-- test: fail; anyof=error during connect||Cannot connect to the Docker daemon -->
```bash
export DOCKER_HOST=tcp://127.0.0.1:2375
docker info --format '{{.ServerVersion}}' 2>&1
```

Find the cause, fix it, and prove the engine is reachable.

<details><summary>Solution</summary>

The error names the address the client tried: `127.0.0.1:2375`. Docker Desktop and a default Linux installation do
not listen on TCP, so a `DOCKER_HOST` left over from an old setup is the cause. Check it, remove it, verify:

<!-- test: contains=reachable -->
```bash
export DOCKER_HOST=tcp://127.0.0.1:2375
echo "DOCKER_HOST=$DOCKER_HOST"
unset DOCKER_HOST
docker info --format '{{.ServerVersion}}' > /dev/null && echo "engine reachable"
```

In a real terminal, also remove the `export DOCKER_HOST=…` line from the shell profile (`~/.bashrc`, `~/.zshrc`) so
it does not come back in the next terminal.

</details>

## Real-world scenario

A new team member says: "The API works on my laptop but crashes on the test server with `ModuleNotFoundError`." The
team currently deploys by copying the code to the server and running `pip install` there. What is going on, and what
would you propose?

<details><summary>Model answer</summary>

The server's environment differs from the laptop's: a library is missing or installed in another version, because each
environment is prepared by hand and drifts (lesson 002). Propose packaging the application as an image built once from
pinned dependencies (`requirements.txt`), tested in CI, and deployed unchanged to every server: the test server then
runs exactly what was tested. The servers only need Docker installed.

</details>

## Cleanup

Nothing to clean: every container was started with `--rm`.
