# Lesson 089 · Multi-stage builds for Go

> Level 14 · Multi-stage builds · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

A static Go binary needs no runtime, no shell and no C library, so its final stage can be almost empty.
**Distroless** images (`gcr.io/distroless/static-debian12`) contain only what such a program may still need: CA
certificates for HTTPS, time zone data, `/etc/passwd` with a non-root user. No shell, no package manager. The image
shrinks to little more than the binary, and an attacker who gets into the process finds no tools. The price: you
cannot `docker exec … sh` into it, and every command must be in exec form.

## Visual

```text
  stage "build" golang:1.26-alpine                      final  gcr.io/distroless/static-debian12:nonroot
  ┌───────────────────────────────────────────┐         ┌───────────────────────────────────────────────┐
  │ go mod download                           │         │ /go-api            (the program)              │
  │ CGO_ENABLED=0 go build -trimpath          │──COPY──▶│ /etc/ssl/certs     (CA certificates)          │
  │   -ldflags="-s -w" -o /out/go-api         │         │ /usr/share/zoneinfo, /etc/passwd (nonroot)    │
  └───────────────────────────────────────────┘         │ no /bin/sh, no apk/apt, no busybox            │
                                                        └───────────────────────────────────────────────┘
   single stage ≈ 490 MB   ·   multi-stage on alpine ≈ 26 MB   ·   multi-stage on distroless ≈ 15 MB
   (disk usage measured in lessons 087 and 089; yours may differ slightly)
```

| Final base | Contains | Use when |
|---|---|---|
| `scratch` | nothing at all | the binary needs no certificates, users or time zones |
| `gcr.io/distroless/static-debian12:nonroot` | CA certs, tzdata, passwd, non-root user | static binaries (Go, Rust) |
| `alpine:3.23` | a shell and `apk` | you need tools in the image (debugging, scripts) |

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-089 examples/go-api
cp 13-multistage/089-multistage-go/examples/Dockerfile* ~/docker-practice/lesson-089/
cd ~/docker-practice/lesson-089
cat Dockerfile
```

## Demonstration

<!-- test: contains=go-distroless; output -->
```bash
docker build -q -t go-distroless:1.0 . > /dev/null
docker image ls go-distroless
```

```text
IMAGE               ID             DISK USAGE   CONTENT SIZE   EXTRA
go-distroless:1.0   145a89eb0490       14.7MB         3.26MB        
```

<!-- test: contains=Up -->
```bash
docker run -d --name go-distroless -p 8091:8080 go-distroless:1.0 > /dev/null
docker ps --filter name=go-distroless --format '{{.Names}}: {{.Status}}'
```

<!-- test: retry=10; contains=Hello from Go; output -->
```bash
curl -s http://localhost:8091/
```

```text
{"hostname":"d6dd6114f5b4","message":"Hello from Go"}
```

The image's configuration shows the non-root user it inherited from the `:nonroot` base:

<!-- test: contains=65532; output -->
```bash
docker image inspect --format 'user={{.Config.User}} entrypoint={{.Config.Entrypoint}}' go-distroless:1.0
```

```text
user=65532 entrypoint=[/go-api]
```

And there is no shell to get into:

<!-- test: fail; contains=executable file not found; output -->
```bash
docker exec go-distroless sh 2>&1
```

```text
OCI runtime exec failed: exec failed: unable to start container process: exec: "sh": executable file not found in $PATH
```

## Command breakdown

| Instruction / flag | Meaning |
|---|---|
| `-trimpath` | remove local file system paths from the binary (reproducible builds) |
| `-ldflags="-s -w"` | strip the symbol table and debug information: a smaller binary |
| `FROM gcr.io/distroless/static-debian12:nonroot` | minimal base with a non-root default user (uid 65532) |
| `ENTRYPOINT ["/go-api"]` | exec form: started directly, no shell involved |
| `docker image inspect --format '{{.Config.User}}'` | the user the image runs as by default |

## Hands-on lab

**Instructions.** Compare the binary built with and without `-ldflags="-s -w"`. Build the `build` stage, then build the
same program once more inside it without the flags, and list both files.

**Expected result.** The stripped binary is noticeably smaller (often around 30 %); both run the same code.

**Verification.**

<!-- test: contains=/out/go-api; contains=/tmp/go-api-full -->
```bash
docker build -q --target build -t go-distroless:build . > /dev/null
docker run --rm go-distroless:build sh -c 'CGO_ENABLED=0 go build -o /tmp/go-api-full . && ls -l /out/go-api /tmp/go-api-full'
```

## Break it

`Dockerfile.broken` writes the entrypoint in **shell form** (`ENTRYPOINT /go-api`), as many Dockerfiles do:

<!-- test: fail; contains=/bin/sh; output -->
```bash
docker build -q -f Dockerfile.broken -t go-distroless:broken . > /dev/null 2>&1
docker run -d --name go-broken go-distroless:broken 2>&1
```

```text
1c81475136461650e092b8d08f6447a8a9ea86dce09cefb9762121b4a7c927cd
docker: Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: error during container init: exec: "/bin/sh": stat /bin/sh: no such file or directory

Run 'docker run --help' for more information
```

## Troubleshoot it

`exec: "/bin/sh": stat /bin/sh: no such file or directory`: Docker tried to start `/bin/sh`, not `/go-api`. The shell
form `ENTRYPOINT /go-api` means "run `/bin/sh -c "/go-api"`", and distroless has no `/bin/sh`. The image configuration
shows it:

<!-- test: contains=/bin/sh; output -->
```bash
docker image inspect --format '{{json .Config.Entrypoint}}' go-distroless:broken
```

```text
["/bin/sh","-c","/go-api"]
```

The build even warned about it (`JSONArgsRecommended`), but warnings scroll past easily.

## Fix it

Use the exec form, a JSON array, as `Dockerfile` does:

<!-- test: contains=["/go-api"] -->
```bash
docker rm -f go-broken > /dev/null 2>&1 || true
docker build -q -t go-distroless:fixed . > /dev/null
docker image inspect --format '{{json .Config.Entrypoint}}' go-distroless:fixed
```

## Practice challenge

Without a shell in the image, how do you debug the running `go-distroless` container's network? Start a throw-away
`busybox:1.37` container that **shares its network namespace** (`--network container:NAME`) and call the API's
`/health` endpoint on `localhost` from there.

<details>
<summary>Solution</summary>

<!-- test: contains="status":"ok"; output -->
```bash
docker run --rm --network container:go-distroless busybox:1.37 wget -qO- http://localhost:8080/health
```

```text
{"status":"ok"}
```

The debug container sees the same network interfaces and `localhost` as the distroless one, with all of BusyBox's
tools. Docker Desktop also offers `docker debug`, which attaches a toolbox to a running container in a similar way.
Lesson 052 uses this technique for network troubleshooting.

</details>

## Real-world example

Kubernetes controllers, CLIs and many cloud-native services written in Go ship as distroless or `scratch` images of a
few MB. Security teams like them: a vulnerability scan of the image (lesson 082) has almost nothing to report, because
there are no OS packages. Debugging moves out of the image into ephemeral debug containers
(`kubectl debug` in Kubernetes, the busybox trick here).

## Recap

- Static Go binaries run on `distroless/static` (or `scratch`): images of a few MB.
- `:nonroot` distroless images run as uid 65532 by default.
- No shell: `ENTRYPOINT`/`CMD` must use the exec form (JSON array), and `docker exec … sh` is impossible.
- Debug through a sidecar container that shares the network namespace (`--network container:NAME`).

## Cleanup

<!-- test -->
```bash
docker rm -f go-distroless go-broken > /dev/null 2>&1 || true
docker image rm -f go-distroless:1.0 go-distroless:build go-distroless:broken go-distroless:fixed > /dev/null 2>&1 || true
rm -rf ~/docker-practice/lesson-089
```

Next: [Lesson 090 · Multi-stage builds for Java](../090-multistage-java/README.md)
