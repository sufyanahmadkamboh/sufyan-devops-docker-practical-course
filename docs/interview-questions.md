# Docker interview questions

Questions asked in DevOps, platform and backend interviews, from fundamentals to production. Answer out loud first,
then open the model answer; the lesson link has the hands-on version.

## Fundamentals

**1. What is the difference between a container and a virtual machine?**
<details><summary>Answer</summary>

A VM emulates hardware and runs a full guest OS with its own kernel; a container is an isolated process sharing the
host's kernel (namespaces for isolation, cgroups for limits). Containers start in under a second and weigh megabytes;
VMs isolate more strongly. In the cloud, containers usually run inside VMs. → [003](../01-fundamentals/003-docker-vs-vms/README.md)
</details>

**2. What is the difference between an image and a container?**
<details><summary>Answer</summary>

An image is a read-only template of layers plus metadata; a container is a running instance with its own writable
layer on top. Many containers can run from one image; deleting a container deletes its writable layer, not the image.
→ [007](../02-containers/007-images-vs-containers/README.md)
</details>

**3. Walk through what happens when you run `docker run nginx`.**
<details><summary>Answer</summary>

The CLI sends API requests to `dockerd`. If the image is not local, the daemon pulls it from the registry (resolving
the tag to a digest, downloading missing layers). It creates the container (writable layer, network endpoint,
configuration), then containerd and runc create the namespaces and cgroups and start the image's
ENTRYPOINT/CMD as PID 1. → [004](../01-fundamentals/004-docker-architecture/README.md)
</details>

**4. A container exits immediately after `docker run -d`. Why, and how do you find out?**
<details><summary>Answer</summary>

A container lives as long as its main process. Either the command finished (a shell with nothing to do, a one-off
script) or it crashed. `docker ps -a` shows the exit code, `docker logs` the output, `docker inspect` the command and
`.State.Error`. Exit code 127 is "command not found", 137 a SIGKILL (often out of memory).
→ [troubleshooting problem 01](../17-troubleshooting/README.md)
</details>

**5. What do the exit codes 0, 1, 125, 126, 127, 137 and 143 mean?**
<details><summary>Answer</summary>

0 success; 1 the application failed; 125 Docker itself failed (bad option); 126 the command is not executable; 127
the command was not found; 137 = 128 + 9, killed with SIGKILL (out of memory, or `docker kill`, or a stop timeout);
143 = 128 + 15, terminated with SIGTERM (a normal `docker stop` the application handled).
→ [009](../02-containers/009-container-lifecycle/README.md)
</details>

## Images and Dockerfiles

**6. What is the difference between CMD and ENTRYPOINT?**
<details><summary>Answer</summary>

ENTRYPOINT is the executable; CMD is its default arguments (or the default command when there is no ENTRYPOINT).
`docker run IMAGE ARGS` replaces CMD; replacing ENTRYPOINT needs `--entrypoint`. Use the exec form (JSON array) so the
process is PID 1 and receives signals. → [029](../04-dockerfiles/029-cmd-and-entrypoint/README.md)
</details>

**7. What is the difference between ARG and ENV? Can you use ARG for a password?**
<details><summary>Answer</summary>

ARG exists only during the build; ENV is stored in the image and present at run time. Neither is safe for secrets:
ARG values used in a `RUN` appear in `docker history`, and ENV is visible in `docker inspect`. Use BuildKit build
secrets (`--secret`) at build time and runtime secrets (files) at run time.
→ [031](../04-dockerfiles/031-arg/README.md), [083](../12-security/083-secrets-in-images/README.md)
</details>

**8. How does the build cache work, and how do you order a Dockerfile for it?**
<details><summary>Answer</summary>

Each instruction's result is cached; a step is reused while it and all previous steps are unchanged (for `COPY`, the
copied files' content). Once a step changes, every later step reruns. So: base image, then system packages, then
dependency manifests (`package.json`, `requirements.txt`) and their install, and the frequently changing source code
last. → [039](../05-builds/039-build-cache/README.md)
</details>

**9. Why does `.dockerignore` matter?**
<details><summary>Answer</summary>

It keeps files out of the build context: faster builds (less to send), fewer cache invalidations, and no accidental
`COPY . .` of `.git`, `.env`, keys or `node_modules` into the image. → [037](../05-builds/037-dockerignore/README.md)
</details>

**10. Why is the `latest` tag dangerous?**
<details><summary>Answer</summary>

It is only the default tag, not "the newest", and it moves: the same name means different images on different days
and machines, so builds and deployments are not reproducible and rollbacks are unclear. Pin versions
(`nginx:1.30-alpine`) and deploy by digest. → [021](../03-images/021-latest-tag-danger/README.md)
</details>

**11. What is a multi-stage build and why use it?**
<details><summary>Answer</summary>

Several `FROM` stages in one Dockerfile: compile in a stage with the full toolchain, then `COPY --from=build` only the
result into a minimal runtime image. Images become much smaller, with fewer packages to patch and attack, and no
compilers or source code in production. → [087](../13-multistage/087-why-multistage/README.md)
</details>

**12. How do you make an image smaller?**
<details><summary>Answer</summary>

Multi-stage builds; a minimal base (alpine, slim, distroless, scratch for static binaries); install only production
dependencies; clean package caches in the same `RUN`; `.dockerignore`; and measure with `docker image ls` and
`docker history` to find the big layers. → [091](../13-multistage/091-measuring-image-size/README.md)
</details>

## Networking and storage

**13. What is the difference between `EXPOSE` and `-p`?**
<details><summary>Answer</summary>

`EXPOSE` only documents the port the application listens on. `-p HOST:CONTAINER` actually publishes it on the host.
Containers on the same network reach each other on any port without either.
→ [051](../07-networking/051-expose-vs-publish/README.md)
</details>

**14. Why can't two containers on the default bridge reach each other by name?**
<details><summary>Answer</summary>

Only user-defined networks have Docker's embedded DNS (127.0.0.11) for container names. Create a network and attach
both containers; Compose does this automatically for every project.
→ [048](../07-networking/048-custom-networks/README.md), [050](../07-networking/050-container-dns/README.md)
</details>

**15. The port is published but the application is not reachable. What do you check?**
<details><summary>Answer</summary>

`docker ps` for the mapping and that it is running; `docker logs` for the address it listens on: an application
bound to `127.0.0.1` inside the container is unreachable from outside it, it must listen on `0.0.0.0`; that the
container port in `-p` is the one the application really uses; and the host firewall or a port conflict.
→ [052](../07-networking/052-network-troubleshooting/README.md)
</details>

**16. Volumes vs bind mounts: when do you use which?**
<details><summary>Answer</summary>

Named volumes for data Docker should manage (databases, uploads): portable, independent of the host's folder layout,
initialized from the image. Bind mounts for files you control on the host: source code in development, a config
file. → [057](../08-storage/057-volumes-vs-bind-mounts/README.md)
</details>

**17. A database container was recreated and the data is gone. What happened?**
<details><summary>Answer</summary>

The data was in the container's writable layer (no volume, or the volume mounted at the wrong path), which is deleted
with the container. Mount a named volume at the database's data directory and verify it with `docker inspect`
(`.Mounts`). → [058](../08-storage/058-persistent-database/README.md)
</details>

## Compose

**18. Does `depends_on` wait until the database is ready?**
<details><summary>Answer</summary>

Not by default: it only orders container start. Add a healthcheck to the database and use
`depends_on: db: condition: service_healthy`; applications should also retry connections, because dependencies can
restart later. → [068](../10-compose/068-depends-on-vs-readiness/README.md)
</details>

**19. What does `docker compose down -v` remove that `down` keeps?**
<details><summary>Answer</summary>

The project's named volumes, and with them the data. `down` removes containers and networks only.
→ [074](../10-compose/074-compose-up-down/README.md)
</details>

## Security

**20. Why should containers not run as root?**
<details><summary>Answer</summary>

Root in the container is root on the kernel, only limited by namespaces, capabilities and seccomp. A vulnerability
in the application then starts with root privileges: it can change any file of the container, use the remaining
capabilities, and is one kernel or misconfiguration bug from the host. Add a user and `USER` it.
→ [081](../12-security/081-non-root-users/README.md)
</details>

**21. Why is access to `/var/run/docker.sock` equivalent to root on the host?**
<details><summary>Answer</summary>

Whoever can talk to the daemon can start a privileged container that mounts the host's root file system. Never mount
the socket into application containers; the `docker` group on Linux is root-equivalent.
→ [080](../12-security/080-attack-surface/README.md)
</details>

**22. How would you harden a container at run time?**
<details><summary>Answer</summary>

Non-root user; `--read-only` with tmpfs for the paths that must be writable; `--cap-drop ALL` and add back only what
is needed; `--security-opt no-new-privileges`; memory, CPU and process limits; no privileged mode, no Docker socket;
only the ports it needs, published to the right interface.
→ [084](../12-security/084-read-only-filesystems/README.md), [085](../12-security/085-linux-capabilities/README.md)
</details>

**23. How do secrets leak into images, and how do you prevent it?**
<details><summary>Answer</summary>

`COPY` of a key or `.env` file (even if deleted in a later layer, it stays in the earlier one); `ARG`/`ENV` values
(visible in `docker history` / `docker inspect`). Prevent with `.dockerignore`, BuildKit `--secret` mounts for build
time and runtime secret files for run time, and by scanning images.
→ [083](../12-security/083-secrets-in-images/README.md)
</details>

## Operations

**24. A container is "Up" but the service does not answer. How can Docker know?**
<details><summary>Answer</summary>

Running only means the process exists. A HEALTHCHECK runs a real check (an HTTP request, `pg_isready`) and marks the
container `healthy` or `unhealthy`; orchestrators and Compose can act on it.
→ [093](../14-observability/093-running-is-not-healthy/README.md)
</details>

**25. A container keeps restarting with exit code 137. What do you check?**
<details><summary>Answer</summary>

`docker inspect --format '{{.State.OOMKilled}}'`: true means the memory limit was exceeded. Compare usage in
`docker stats` with the limit; fix the leak or the configuration (for example a JVM heap larger than the limit), or
raise the limit deliberately. → [099](../15-resources/099-memory-pressure/README.md)
</details>

**26. How do you build one image for both amd64 and arm64?**
<details><summary>Answer</summary>

`docker buildx build --platform linux/amd64,linux/arm64 -t NAME --push .` with a builder that supports both (QEMU
emulation or native nodes). The registry stores an image index; each host pulls its own platform.
→ [104](../16-advanced/104-multi-architecture-images/README.md)
</details>

**27. What does a production-ready Dockerfile look like?**
<details><summary>Answer</summary>

Pinned base image (tag or digest), multi-stage, dependencies installed before the source for caching, production
dependencies only, non-root `USER`, exec-form `ENTRYPOINT`/`CMD`, a `HEALTHCHECK` where the platform uses it, labels
(version, source), no secrets, `.dockerignore`, and configuration from the environment.
→ [130](../18-production/130-production-dockerfile/README.md)
</details>

**28. How does Docker fit into CI/CD and Kubernetes?**
<details><summary>Answer</summary>

CI builds the image once from the commit, tests and scans it, and pushes it to a registry with an immutable tag (the
commit SHA or a version). Every environment deploys that same image by tag or digest; Kubernetes pulls it and runs it
as Pods, with the same concepts: ports, environment, volumes, probes, resource limits, the user.
→ [135](../19-ci-cd/135-docker-in-ci/README.md), [138](../20-kubernetes/138-from-docker-to-kubernetes/README.md)
</details>
