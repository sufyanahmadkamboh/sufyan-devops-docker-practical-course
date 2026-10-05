# Project 04 · Go API, as small as it gets

> ⏱ 45 minutes · run every command from the course folder

## Goal

Go compiles to a single static binary, so a Go service needs almost nothing at run time. Build the Go API
([examples/go-api](../../examples/go-api)) three ways (single stage, distroless, `scratch`), **measure** the
difference, and ship the image that is both tiny and safe.

## Requirements

- [ ] A multi-stage build: compile in `golang:1.26-alpine`, run on `gcr.io/distroless/static-debian12:nonroot`
- [ ] The binary is static (`CGO_ENABLED=0`) and stripped (`-ldflags="-s -w"`)
- [ ] The final image has no shell and runs as a non-root user
- [ ] Image sizes of the three variants are measured, not guessed
- [ ] The API answers on `/` and `/health`

## Architecture

```text
 golang:1.26-alpine  (compiler, source, module cache)            final image
 ┌──────────────────────────────────────────┐                    ┌──────────────────────────────┐
 │ go build  CGO_ENABLED=0 -trimpath -s -w  │ ── /out/go-api ──▶ │ distroless static :nonroot   │
 └──────────────────────────────────────────┘    (one file)      │   /go-api   user 65532       │
                                                                 │   no shell, no apk           │
                                                                 └──────────────────────────────┘
```

## Build it

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh project-04 examples/go-api
cp -r 21-projects/04-go-api/solution/. ~/docker-practice/project-04/
cd ~/docker-practice/project-04
ls -A
```

<!-- test: contains=distroless; output -->
```bash
cat Dockerfile
```

```text
# syntax=docker/dockerfile:1
# Stage 1: compile a static binary (no C library needed: CGO_ENABLED=0).
FROM golang:1.26-alpine AS build
WORKDIR /src
COPY go.mod ./
RUN go mod download
COPY *.go ./
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/go-api .

# Stage 2: only the binary, on distroless static: no shell, no package manager, user 65532.
FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /out/go-api /go-api
EXPOSE 8080
ENTRYPOINT ["/go-api"]
```

Build all three variants:

<!-- test: contains=go-api -->
```bash
docker build -q -t go-api:single -f Dockerfile.single . > /dev/null
docker build -q -t go-api:distroless . > /dev/null
docker build -q -t go-api:scratch -f Dockerfile.scratch . > /dev/null
docker image ls --format '{{.Repository}}:{{.Tag}}' go-api
```

## Verify

The measured sizes:

<!-- test: contains=go-api:distroless; output -->
```bash
for tag in single distroless scratch; do
  docker image inspect --format "go-api:$tag {{.Size}}" go-api:$tag
done | awk '{ printf "%-18s %6.1f MB\n", $1, $2 / 1000000 }'
```

```text
go-api:single        98.0 MB
go-api:distroless     3.3 MB
go-api:scratch        2.5 MB
```

(`.Size` is the image's content size, the compressed layers a pull downloads; `docker image ls` also shows the
unpacked disk usage.) The single-stage image carries the whole Go toolchain to production. The distroless one adds
only a few files to the binary (CA certificates, time zones, `/etc/passwd` with the `nonroot` user); `scratch` is the
binary alone.

Run the distroless image and use it:

<!-- test: contains=Hello from Go; retry=10 -->
```bash
docker run -d --name go-api -p 8084:8080 go-api:distroless > /dev/null
curl -s http://localhost:8084/
```

<!-- test: contains=65532; output -->
```bash
docker inspect --format 'user={{.Config.User}}' go-api:distroless
docker image inspect --format '{{.Config.User}}' gcr.io/distroless/static-debian12:nonroot
```

```text
user=65532
65532
```

No shell to break into:

<!-- test: anyof=executable file not found||no such file or directory; output -->
```bash
docker exec go-api sh 2>&1 || true
```

```text
OCI runtime exec failed: exec failed: unable to start container process: exec: "sh": executable file not found in $PATH
```

## Break it and fix it

[Dockerfile.broken](solution/Dockerfile.broken) is the distroless image with one line written differently:
`CMD /go-api` instead of `ENTRYPOINT ["/go-api"]`.

<!-- test: contains=/bin/sh; output -->
```bash
docker build -q -t go-api:broken -f Dockerfile.broken . > /dev/null
docker run --name go-api-broken go-api:broken 2>&1 | grep -m1 "Error response" || true
docker image inspect --format 'Cmd: {{json .Config.Cmd}}' go-api:broken
```

```text
docker: Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: error during container init: exec: "/bin/sh": stat /bin/sh: no such file or directory
Cmd: ["/bin/sh","-c","/go-api"]
```

The **shell form** (`CMD command`) means "run this with `/bin/sh -c`", and the distroless image has no `/bin/sh`.
The container cannot even start. Use the exec form (a JSON array), which runs the binary directly:

<!-- test -->
```bash
docker rm -f go-api-broken > /dev/null
sed -i.bak 's|^CMD /go-api$|ENTRYPOINT ["/go-api"]|' Dockerfile.broken
docker build -q -t go-api:broken -f Dockerfile.broken . > /dev/null
docker run -d --name go-api-broken -p 8085:8080 go-api:broken > /dev/null
```

<!-- test: contains=Hello from Go; retry=10 -->
```bash
curl -s http://localhost:8085/
```

## Stretch goals

- Add a `-healthcheck` flag to the binary (as the capstone's API does) and a `HEALTHCHECK` that uses it: the image
  has no `curl` or `wget`.
- Build for `linux/arm64` too with `docker buildx build --platform linux/amd64,linux/arm64` (lesson 104).
- Compare the build time of a second build after changing only `main.go`: which layers come from the cache?

## Cleanup

<!-- test -->
```bash
docker rm -f go-api go-api-broken > /dev/null 2>&1 || true
docker image rm -f go-api:single go-api:distroless go-api:scratch go-api:broken > /dev/null
cd ~ && rm -rf ~/docker-practice/project-04
```

Next: [Project 05 · Java API on a JRE](../05-java-api/README.md)
