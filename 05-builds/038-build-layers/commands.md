<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 038 · Build layers · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-038 05-builds/038-build-layers/examples
cd ~/docker-practice/lesson-038
cat Dockerfile
```

## Demonstration

```bash
docker build -q -t layers:demo . > /dev/null
docker history --format '{{.Size}}\t{{.CreatedBy}}' layers:demo
```

```bash
docker run --rm layers:demo
```

## Hands-on lab

```bash
for image in alpine:3.23 layers:demo; do
  echo "$image $(docker image inspect --format '{{len .RootFS.Layers}}' "$image")"
done
```

## Break it

```bash
cat Dockerfile.wasteful
docker build -q -f Dockerfile.wasteful -t layers:wasteful . > /dev/null
docker image ls layers:wasteful
```

## Troubleshoot it

```bash
docker run --rm layers:wasteful ls /tmp/download.bin 2>&1 || true
```

```bash
docker history --format '{{.Size}}\t{{.CreatedBy}}' layers:wasteful | head -3
```

## Fix it

```bash
docker build -q -f Dockerfile.fixed -t layers:fixed . > /dev/null
docker image ls layers
```

## Practice challenge

```bash
docker history --no-trunc --format '{{.Size}}\t{{.CreatedBy}}' node:24-alpine | sort -h | tail -1 | cut -c1-90
```

## Cleanup

```bash
docker image rm -f layers:demo layers:wasteful layers:fixed > /dev/null
rm -rf ~/docker-practice/lesson-038
```
