<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 103 · BuildKit and buildx · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A script builds the build stage with a typo:

```bash
docker buildx build --target biuld -t cafe-go:build-stage . 2>&1 | grep ERROR
test "${PIPESTATUS[0]}" -eq 0
```

```text
ERROR: failed to build: failed to solve: target stage "biuld" could not be found (did you mean build?)
```

## Troubleshoot it

BuildKit reads the whole Dockerfile before it builds anything, and refuses a target that is not one of the stage
names given with `AS`. List them:

```bash
grep -n ' AS ' Dockerfile
```

```text
2:FROM golang:1.26-alpine AS build
8:FROM scratch AS export
12:FROM gcr.io/distroless/static-debian12:nonroot AS image
```

## Fix it

```bash
docker buildx build -q --target build -t cafe-go:build-stage --load . > /dev/null
docker image ls cafe-go --format '{{.Repository}}:{{.Tag}}'
```
