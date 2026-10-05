# Troubleshooting problem 18 · Huge image

> ⏱ 20 minutes · run every command from the course folder · related lessons: 017, 087, 089, 091

## Problem

The Go API is a single small binary, but its image is hundreds of megabytes. Deployments are slow because every new
server downloads it, and the security scanner reports findings in tools the API never uses.

## Symptoms

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh trouble-18 examples/go-api
cp 17-troubleshooting/18-huge-image/examples/*.Dockerfile ~/docker-practice/trouble-18/
cd ~/docker-practice/trouble-18
ls
```

<!-- test: contains=go-api:fat; output -->
```bash
docker build -q -f broken.Dockerfile -t go-api:fat . > /dev/null
docker image ls go-api:fat --format '{{.Repository}}:{{.Tag}}  {{.Size}}'
```

```text
go-api:fat  492MB
```

## Investigation

**1. Which layers are big?** `docker history` lists every layer with its size and the instruction that created it:

<!-- test: contains=go build; output -->
```bash
docker history --format '{{.Size}}\t{{.CreatedBy}}' go-api:fat | cut -c1-100 | head -12
```

```text
0B	CMD ["api"]
0B	EXPOSE [8080/tcp]
102MB	RUN /bin/sh -c go build -o /usr/local/bin/ap…
24.6kB	COPY . . # buildkit
8.19kB	WORKDIR /src
4.1kB	WORKDIR /go
16.4kB	RUN /bin/sh -c mkdir -p "$GOPATH/src" "$GOPA…
282MB	COPY /target/ / # buildkit
0B	ENV PATH=/go/bin:/usr/local/go/bin:/usr/loca…
0B	ENV GOPATH=/go
0B	ENV GOTOOLCHAIN=local
0B	ENV GOLANG_VERSION=1.26.8
```

Most of it comes from the base image (`golang:1.26-alpine`): the Go compiler, its standard library sources and
build tools. The `go build` layer is also far bigger than the binary itself (listed below): it contains Go's build
cache (`/root/.cache/go-build`) as well.

**2. What else is inside?** Everything a build needs, nothing a server needs:

<!-- test: contains=go version; contains=main.go; output -->
```bash
docker run --rm go-api:fat go version
docker run --rm go-api:fat ls /src
docker run --rm go-api:fat sh -c 'ls -l /usr/local/bin/api'
```

```text
go version go1.26.8 linux/amd64
broken.Dockerfile
fixed.Dockerfile
go.mod
main.go
-rwxr-xr-x    1 root     root       8624989 Oct  5 10:31 /usr/local/bin/api
```

## Commands

| Command | What it tells you |
|---|---|
| `docker image ls IMAGE --format '{{.Size}}'` | the image size |
| `docker history IMAGE` | the size of every layer and the instruction behind it |
| `docker run --rm IMAGE ls / …` | what the image contains (compilers, sources, caches, package managers) |
| `docker image inspect --format '{{.Config.User}}'` | the user, often root in build images ([problem 20](../20-running-as-root/README.md)) |

## Output interpretation

An image is the sum of its layers, including every layer of its base image (lesson 017). The binary is small; the
toolchain around it is not. Size is not only disk space: every package is something to patch and a tool an attacker
could use, and every node pulls the full image.

## Root cause

The image was built in a single stage from the compiler image, so the build environment (compiler, sources, shell,
package manager) ships to production with the binary.

## Fix

A multi-stage build (lessons 087, 089): compile in the `golang` stage, copy only the static binary into a minimal,
non-root runtime image.

<!-- test: contains=AS build; output -->
```bash
grep -n '^FROM\|^COPY\|^USER' fixed.Dockerfile
```

```text
2:FROM golang:1.26-alpine AS build
4:COPY go.mod ./
5:COPY *.go ./
8:FROM gcr.io/distroless/static-debian12:nonroot
9:COPY --from=build /out/api /api
10:USER nonroot:nonroot
```

<!-- test: contains=go-api:slim; output -->
```bash
docker build -q -f fixed.Dockerfile -t go-api:slim . > /dev/null
docker image ls go-api --format '{{.Repository}}:{{.Tag}}  {{.Size}}'
```

```text
go-api:slim  14.7MB
go-api:fat  492MB
```

## Verification

The small image does the same job, with no shell, no compiler and no root user:

<!-- test -->
```bash
docker run -d --name go-api -p 8080:8080 go-api:slim > /dev/null
```

<!-- test: retry=10; contains=Hello from Go; output -->
```bash
curl -s http://localhost:8080
```

```text
{"hostname":"d91d39361b3a","message":"Hello from Go"}
```

<!-- test: fail; contains=executable file not found; output -->
```bash
docker exec go-api sh 2>&1
```

```text
OCI runtime exec failed: exec failed: unable to start container process: exec: "sh": executable file not found in $PATH
```

## Prevention

- Use multi-stage builds for every compiled language (Go, Java, Rust, .NET) and for front-end builds (Node.js →
  Nginx), lessons 087–090.
- Choose the smallest base that works: `distroless`, `-alpine`, `-slim`; avoid full OS images for runtime.
- Keep `.dockerignore` tight so sources, tests and `.git` never enter the image (lesson 037).
- Track image size in CI and fail the build when it grows unexpectedly (lesson 091).

## Cleanup

<!-- test -->
```bash
docker rm -f go-api > /dev/null
docker image rm go-api:fat go-api:slim > /dev/null
rm -rf ~/docker-practice/trouble-18
```

Next: [Problem 19 · Dockerfile security issue](../19-dockerfile-security-issue/README.md)
