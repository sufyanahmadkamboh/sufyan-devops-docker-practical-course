<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 042 · Containerizing a Go application · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

`Dockerfile.broken` forgets to copy `go.mod`:

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

```bash
grep COPY Dockerfile.broken
ls
```

## Fix it

Copy `go.mod` (and `go.sum`, when the module has dependencies) before building, as `Dockerfile` does:

```bash
docker build -q -t go-api:fixed . > /dev/null
docker run --rm -d --name go-fixed -p 8086:8080 go-api:fixed > /dev/null
sleep 1
curl -s http://localhost:8086/
docker rm -f go-fixed > /dev/null
```
