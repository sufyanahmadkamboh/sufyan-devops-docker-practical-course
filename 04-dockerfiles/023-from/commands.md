<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 023 · FROM: choosing a base image · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-023
cd ~/docker-practice/lesson-023
```

## Demonstration

```bash
for image in busybox:1.37 alpine:3.23 debian:13-slim ubuntu:24.04 gcr.io/distroless/static-debian12:nonroot; do
  docker image ls --format '{{.Size}}\t{{.Repository}}:{{.Tag}}' "$image"
done
```

```bash
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.Size}}' python
```

```bash
for image in alpine:3.23 debian:13-slim ubuntu:24.04; do
  tools=$(docker run --rm "$image" sh -c 'for t in sh bash apk apt-get curl; do command -v $t > /dev/null && printf "%s " $t; done; true')
  echo "$image: $tools"
done
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-023
printf 'FROM debian:13-slim\nCMD ["grep", "PRETTY_NAME", "/etc/os-release"]\n' > Dockerfile.debian
docker build -q -f Dockerfile.debian -t base-demo:debian . > /dev/null
docker run --rm base-demo:debian
```

## Break it

```bash
printf 'FROM alpine:3.23\nRUN bash -c "echo preparing the image"\n' > Dockerfile.alpine
docker build --progress=plain -f Dockerfile.alpine -t base-demo:alpine . 2>&1 | grep -E 'not found|ERROR'
```

## Troubleshoot it

```bash
docker run --rm alpine:3.23 sh -c 'command -v bash || echo "no bash"; ls -l /bin/sh'
```

## Fix it

```bash
printf 'FROM alpine:3.23\nRUN sh -c "echo preparing the image"\n' > Dockerfile.alpine
docker build --progress=plain -f Dockerfile.alpine -t base-demo:alpine . 2>&1 | grep "preparing the image"
```

## Practice challenge

```bash
docker run --rm alpine:3.23 sh -c 'ls /lib | grep "^ld-"'
docker run --rm debian:13-slim sh -c 'ls /lib64 /lib/x86_64-linux-gnu 2>/dev/null | grep "^ld-" | head -1'
```

## Cleanup

```bash
docker image rm -f base-demo:debian base-demo:alpine > /dev/null
rm -rf ~/docker-practice/lesson-023
```
