<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 087 · Why multi-stage builds? · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Stages are also useful for **tests**. Without changing the final image, add a stage `test` (based on `build`) that runs
`go vet ./...`, and build only that stage with `--target test`. Write the new Dockerfile to `Dockerfile.test`.

## Solution

```bash
cd ~/docker-practice/lesson-087
{ sed -n '1,/^RUN CGO_ENABLED/p' Dockerfile
  printf '\n# a test stage: never shipped, built only with --target test\nFROM build AS test\nRUN go vet ./... && echo "vet passed"\n'
  sed -n '/^# stage 2/,$p' Dockerfile
} > Dockerfile.test
grep -E '^FROM' Dockerfile.test
docker build --progress=plain --no-cache-filter test --target test -f Dockerfile.test -t go-multi:test . 2>&1 | grep -o 'vet passed' | head -1
```

```text
FROM golang:1.26-alpine AS build
FROM build AS test
FROM alpine:3.23
vet passed
```

`FROM build AS test` starts from the build stage's result. A normal `docker build` (no `--target`) skips the test stage,
because the final stage does not depend on it; CI runs `--target test` first, then the full build.
`--no-cache-filter test` makes the test run even when it is cached.
