<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 042 · Containerizing a Go application · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Go cross-compiles by setting `GOOS` and `GOARCH`. Without installing Go, build an **arm64** Linux binary of the API into
the lab folder (a bind mount, `-v "$(pwd):/src"`), and let the Go tool confirm its architecture with `go version -m`.

## Solution

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
