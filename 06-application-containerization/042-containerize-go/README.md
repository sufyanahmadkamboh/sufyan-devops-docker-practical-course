# Lesson 042 · Containerizing a Go application

> Level 7 · Application containerization · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

Go compiles to a single binary. Containerizing it means: compile inside the official Go image (no Go installation on
your computer), with the module files copied first so dependencies are cached, as a **static** binary
(`CGO_ENABLED=0`), and run it as an unprivileged user. This lesson builds a working single-stage image and measures
what it costs: the whole Go toolchain ships with an 8 MB program. Lesson 089 removes it with a multi-stage build.

## Visual

```text
  go-api/                    Dockerfile (single stage)                image go-api:1.0
  ├── go.mod   ──────▶  COPY go.mod ./  +  RUN go mod download        ┌──────────────────────────────┐
  └── main.go  ──────▶  COPY main.go ./                               │ Go toolchain, compiler,      │  ≈ 490 MB
                        RUN CGO_ENABLED=0 go build -o …/go-api .      │ module cache, Alpine         │  that the
                        USER nobody                                   ├──────────────────────────────┤  program
                        CMD ["go-api"]                                │ /usr/local/bin/go-api  ~8 MB │  never uses
                                                                      └──────────────────────────────┘
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-042 examples/go-api
cp 06-application-containerization/042-containerize-go/examples/Dockerfile* ~/docker-practice/lesson-042/
cd ~/docker-practice/lesson-042
ls
```

## Demonstration

<!-- test: contains=go-api; output -->
```bash
docker build -q -t go-api:1.0 . > /dev/null
docker image ls go-api
docker run -d --name go-api -p 8085:8080 go-api:1.0 > /dev/null
```

```text
IMAGE        ID             DISK USAGE   CONTENT SIZE   EXTRA
go-api:1.0   a1141119ce09        492MB           98MB        
```

<!-- test: retry=10; contains=Hello from Go; output -->
```bash
curl -s http://localhost:8085/
```

```text
{"hostname":"5c3d799d1a5d","message":"Hello from Go"}
```

How big is the program itself?

<!-- test: contains=go-api; output -->
```bash
docker run --rm go-api:1.0 ls -lh /usr/local/bin/go-api
```

```text
-rwxr-xr-x    1 root     root        8.2M Oct  5 17:06 /usr/local/bin/go-api
```

## Command breakdown

| Instruction / setting | Why |
|---|---|
| `COPY go.mod ./` (and `go.sum`) then `RUN go mod download` | dependencies in their own cached layer |
| `CGO_ENABLED=0` | pure-Go static binary: no dependency on the C library of the image |
| `go build -o /usr/local/bin/go-api .` | build the package in the current folder into one file |
| `USER nobody` | Alpine's unprivileged user (uid 65534) |
| `CMD ["go-api"]` | exec form: the binary is PID 1 and receives signals |

## Hands-on lab

**Instructions.** Check that the binary is really static: run it in a **different** image that has no Go at all
(`alpine:3.23`), by copying it out of the image with `docker cp`.

**Expected result.** The program starts in plain Alpine and logs `go-api listening on port 8080`.

**Verification.**

<!-- test: contains=go-api listening -->
```bash
cd ~/docker-practice/lesson-042
docker create --name go-extract go-api:1.0 > /dev/null
docker cp go-extract:/usr/local/bin/go-api ./go-api-binary
docker rm go-extract > /dev/null
docker run -d --name go-plain -v "$(pwd)/go-api-binary:/go-api" alpine:3.23 /go-api > /dev/null
sleep 1
docker logs go-plain 2>&1
docker rm -f go-plain > /dev/null
```

`docker create` makes a container without starting it; `docker cp` copies files out of it. This is the manual version
of what a multi-stage build does automatically (lesson 087).

## Break it

`Dockerfile.broken` forgets to copy `go.mod`:

<!-- test: fail; contains=go.mod file not found; output -->
```bash
docker build -f Dockerfile.broken -t go-api:broken . 2>&1 | grep -E 'go: |ERROR' | head -2
test "${PIPESTATUS[0]}" -eq 0
```

```text
#8 0.195 go: go.mod file not found in current directory or any parent directory; see 'go help modules'
#8 ERROR: process "/bin/sh -c CGO_ENABLED=0 go build -o /usr/local/bin/go-api ." did not complete successfully: exit code: 1
```

## Troubleshoot it

`go: go.mod file not found in current directory or any parent directory`: the error comes from the Go tool inside the
`RUN` step (`#8 0.236 go: …`), not from Docker. Docker only reports that the step's command exited with code 1. A
modern Go build needs the module file, and `/src` in the image only contains what the Dockerfile copied. List the
`COPY` lines and compare with the project:

<!-- test: contains=COPY main.go -->
```bash
grep COPY Dockerfile.broken
ls
```

## Fix it

Copy `go.mod` (and `go.sum`, when the module has dependencies) before building, as `Dockerfile` does:

<!-- test: contains=Hello from Go -->
```bash
docker build -q -t go-api:fixed . > /dev/null
docker run --rm -d --name go-fixed -p 8086:8080 go-api:fixed > /dev/null
sleep 1
curl -s http://localhost:8086/
docker rm -f go-fixed > /dev/null
```

## Practice challenge

Go cross-compiles by setting `GOOS` and `GOARCH`. Without installing Go, build an **arm64** Linux binary of the API into
the lab folder (a bind mount, `-v "$(pwd):/src"`), and let the Go tool confirm its architecture with `go version -m`.

<details>
<summary>Solution</summary>

<!-- test: contains=GOARCH=arm64; output -->
```bash
cd ~/docker-practice/lesson-042
docker run --rm -v "$(pwd):/src" -w /src -e CGO_ENABLED=0 -e GOOS=linux -e GOARCH=arm64 golang:1.26-alpine go build -o go-api-arm64 .
docker run --rm -v "$(pwd):/src" -w /src golang:1.26-alpine go version -m go-api-arm64 | grep GOARCH
```

```text
	build	GOARCH=arm64
```

The same source, built for a Raspberry Pi or an AWS Graviton server on an x86 laptop. `docker buildx` uses this to
build multi-architecture images (lesson 104).

</details>

## Real-world example

Go services are among the easiest to containerize well: a static binary needs no runtime, so production images
often contain nothing but the binary and CA certificates. The single-stage image of this lesson is what many teams
start with; the multi-stage version (lesson 089) is what they ship.

## Recap

- Build inside `golang:1.26-alpine`; copy `go.mod`/`go.sum` first and run `go mod download` for caching.
- `CGO_ENABLED=0` produces a static binary that runs on any Linux image.
- A single-stage Go image carries the whole toolchain: hundreds of MB for a program of a few MB.
- `docker create` + `docker cp` copies files out of an image.

## Cleanup

<!-- test -->
```bash
docker rm -f go-api > /dev/null
docker image rm -f go-api:1.0 go-api:fixed > /dev/null
rm -rf ~/docker-practice/lesson-042
```

Next: [Lesson 043 · Containerizing a Java application](../043-containerize-java/README.md)
