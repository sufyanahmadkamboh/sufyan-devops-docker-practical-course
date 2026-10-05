# Glossary

Every term the course uses, in alphabetical order, with the lesson that explains it.

| Term | Meaning | Lesson |
|---|---|---|
| **ARG** | a Dockerfile variable that exists only while the image is built; its value can still be seen in the image history, so never use it for secrets | [031](../04-dockerfiles/031-arg/README.md) |
| **Attack surface** | everything an attacker could use: packages, shells, open ports, privileges, capabilities. Smaller images and fewer privileges shrink it | [080](../12-security/080-attack-surface/README.md) |
| **Base image** | the image a Dockerfile starts from (`FROM`) | [023](../04-dockerfiles/023-from/README.md) |
| **Bind mount** | a host folder or file mounted into a container (`-v "$(pwd):/app"`); changes are visible on both sides | [054](../08-storage/054-bind-mounts/README.md) |
| **Bridge network** | the default network type: a private virtual network on one host, with NAT to the outside | [047](../07-networking/047-default-bridge/README.md) |
| **Build cache** | stored results of earlier build steps; a step is reused while it and every step before it are unchanged | [039](../05-builds/039-build-cache/README.md) |
| **Build context** | the files sent to the builder with `docker build PATH`; `COPY` can only read from it | [036](../05-builds/036-build-context/README.md) |
| **BuildKit** | Docker's build engine: parallel stages, cache mounts, build secrets, multi-platform builds | [103](../16-advanced/103-buildx/README.md) |
| **Buildx** | the CLI for BuildKit (`docker buildx build`), used for multi-platform images and cache export | [103](../16-advanced/103-buildx/README.md) |
| **Capability** | a slice of root's power in Linux (`NET_BIND_SERVICE`, `CHOWN`, …); containers get a reduced set, which you can reduce further with `--cap-drop` | [085](../12-security/085-linux-capabilities/README.md) |
| **cgroups** | the Linux kernel feature that limits and measures a process group's CPU, memory and processes; Docker's resource limits use it | [097](../15-resources/097-cpu-limits/README.md) |
| **CMD** | the default command of an image; replaced by the arguments of `docker run IMAGE ARGS` | [027](../04-dockerfiles/027-cmd/README.md) |
| **Compose project** | the containers, networks and volumes created from one Compose file, named after its folder or `-p` | [063](../10-compose/063-first-compose-file/README.md) |
| **Container** | a running (or stopped) instance of an image: an isolated process with its own writable layer | [007](../02-containers/007-images-vs-containers/README.md) |
| **containerd** | the container runtime the Docker engine uses to run containers; Kubernetes uses it directly | [004](../01-fundamentals/004-docker-architecture/README.md) |
| **Context (Docker)** | a named engine endpoint the client talks to (`docker context ls`) | [004](../01-fundamentals/004-docker-architecture/README.md) |
| **Dangling image** | an image with no tag (`<none>`), usually left over when a tag moved to a newer build | [019](../03-images/019-listing-and-removing-images/README.md) |
| **Digest** | the content hash of an image (`sha256:…`); unlike a tag it always names exactly the same image | [020](../03-images/020-image-tags/README.md) |
| **Distroless** | images with only an application's runtime dependencies: no shell, no package manager | [089](../13-multistage/089-multistage-go/README.md) |
| **Docker daemon (dockerd)** | the engine: the server that builds images and manages containers, networks and volumes | [004](../01-fundamentals/004-docker-architecture/README.md) |
| **Docker Desktop** | Docker for Windows and macOS: the engine runs in a small Linux virtual machine | [005](../01-fundamentals/005-installing-docker/README.md) |
| **Dockerfile** | the recipe of an image: one instruction per step | [022](../04-dockerfiles/022-first-dockerfile/README.md) |
| **.dockerignore** | files and folders left out of the build context | [037](../05-builds/037-dockerignore/README.md) |
| **Embedded DNS** | the resolver at `127.0.0.11` in containers on user-defined networks; it resolves container and service names | [050](../07-networking/050-container-dns/README.md) |
| **ENTRYPOINT** | the fixed executable of an image; `CMD` becomes its default arguments | [028](../04-dockerfiles/028-entrypoint/README.md) |
| **ENV** | an environment variable set in the image, available at build time and at run time | [030](../04-dockerfiles/030-env/README.md) |
| **Exit code** | the number a container's main process ended with: 0 success, 1 application error, 125 Docker error, 126 not executable, 127 command not found, 137 killed (SIGKILL, often out of memory), 143 terminated (SIGTERM) | [009](../02-containers/009-container-lifecycle/README.md) |
| **EXPOSE** | documents which port the application listens on; it publishes nothing | [032](../04-dockerfiles/032-expose/README.md) |
| **Exec form / shell form** | `CMD ["node", "server.js"]` runs the program directly (it receives signals); `CMD node server.js` runs it through `/bin/sh -c` | [027](../04-dockerfiles/027-cmd/README.md) |
| **GHCR** | GitHub Container Registry, `ghcr.io/OWNER/IMAGE` | [079](../11-registry/079-github-container-registry/README.md) |
| **Healthcheck** | a command Docker runs periodically inside a container; it turns "running" into `healthy` or `unhealthy` | [092](../14-observability/092-healthcheck/README.md) |
| **Image** | a read-only template: a stack of file system layers plus metadata (command, environment, ports, user) | [007](../02-containers/007-images-vs-containers/README.md) |
| **Immutable container** | a container that is never changed after it starts: a change means a new image and a new container | [132](../18-production/132-immutable-containers/README.md) |
| **Layer** | one read-only file system change in an image, created by a Dockerfile instruction; layers are shared between images | [017](../03-images/017-image-layers/README.md) |
| **Logging driver** | where a container's output goes: `json-file` (default), `local`, `syslog`, `journald`, … | [102](../16-advanced/102-logging-drivers/README.md) |
| **Manifest list / image index** | one tag pointing to images for several platforms (amd64, arm64); the engine picks its own | [104](../16-advanced/104-multi-architecture-images/README.md) |
| **Multi-stage build** | a Dockerfile with several `FROM` stages; the final image copies only what it needs from earlier stages | [087](../13-multistage/087-why-multistage/README.md) |
| **Named volume** | storage managed by Docker (`-v data:/path`), independent of any container's life | [055](../08-storage/055-named-volumes/README.md) |
| **Namespace** | the Linux kernel feature that gives a process its own view of processes, network, mounts, host name and users | [003](../01-fundamentals/003-docker-vs-vms/README.md) |
| **OCI** | Open Container Initiative: the open standards for image format and runtimes that Docker, containerd and Kubernetes share | [004](../01-fundamentals/004-docker-architecture/README.md) |
| **OOMKilled** | the container was killed by the kernel for exceeding its memory limit (exit code 137) | [098](../15-resources/098-memory-limits/README.md) |
| **PID 1** | the container's main process; it receives the stop signal and the container lives as long as it does | [009](../02-containers/009-container-lifecycle/README.md) |
| **Port publishing** | `-p HOST:CONTAINER` forwards a host port to a container port | [012](../02-containers/012-port-mapping/README.md) |
| **Profile (Compose)** | a label that starts a service only when asked (`--profile debug`) | [070](../10-compose/070-compose-profiles/README.md) |
| **Read-only root file system** | `--read-only`: the container cannot change its own files; writable paths are explicit volumes or tmpfs | [084](../12-security/084-read-only-filesystems/README.md) |
| **Registry** | a server that stores and distributes images (Docker Hub, GHCR, ECR, a private `registry:3`) | [075](../11-registry/075-what-is-a-registry/README.md) |
| **Repository** | a set of images with the same name and different tags (`nginx`, `ghcr.io/team/api`) | [077](../11-registry/077-image-naming/README.md) |
| **Restart policy** | what Docker does when a container stops: `no`, `on-failure`, `unless-stopped`, `always` | [009](../02-containers/009-container-lifecycle/README.md) |
| **Rootless / non-root** | running the container's process as an unprivileged user (`USER`), so a compromise does not start as root | [081](../12-security/081-non-root-users/README.md) |
| **runc** | the low-level runtime that creates a container's namespaces and cgroups, then hands over to the process | [004](../01-fundamentals/004-docker-architecture/README.md) |
| **Secret** | sensitive configuration (passwords, keys) given to a container at run time as a file, never baked into an image | [061](../09-environment-config/061-config-vs-secrets/README.md) |
| **Service (Compose)** | one component of a Compose application; its name is also its DNS name on the project's network | [064](../10-compose/064-compose-services/README.md) |
| **Tag** | a movable name of an image version (`nginx:1.30-alpine`); `latest` is only the default tag, not "the newest" | [020](../03-images/020-image-tags/README.md) |
| **tmpfs** | an in-memory file system mounted into a container, emptied when it stops | [084](../12-security/084-read-only-filesystems/README.md) |
| **USER** | the Dockerfile instruction that sets the user the container runs as | [033](../04-dockerfiles/033-user/README.md) |
| **User-defined network** | a network you create (`docker network create`); unlike the default bridge it provides DNS by container name | [048](../07-networking/048-custom-networks/README.md) |
| **Virtual machine** | an emulated computer with its own kernel, run by a hypervisor; heavier and more isolated than a container | [003](../01-fundamentals/003-docker-vs-vms/README.md) |
| **Volume** | storage outside a container's writable layer that survives the container | [055](../08-storage/055-named-volumes/README.md) |
| **WORKDIR** | the working directory for the following Dockerfile instructions and for the container | [024](../04-dockerfiles/024-workdir/README.md) |
| **Writable layer** | the thin per-container layer on top of the image; deleted with the container | [053](../08-storage/053-writable-layer/README.md) |
