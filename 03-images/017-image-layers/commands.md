<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 017 · Image layers · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-017 03-images/017-image-layers/examples
cd ~/docker-practice/lesson-017
ls
```

## Demonstration

```bash
docker image history nginx:1.30-alpine
```

```bash
echo "$(docker image inspect --format '{{len .RootFS.Layers}}' nginx:1.30-alpine) layers"
```

## Hands-on lab

```bash
echo "$(docker image inspect --format '{{len .RootFS.Layers}}' python:3.14-slim) layers"
docker image history --format '{{.Size}}\t{{.CreatedBy}}' python:3.14-slim | sort -h | tail -3
```

## Break it

```bash
cat broken/Dockerfile
docker build -q -t layers-demo:broken broken > /dev/null
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.Size}}' layers-demo
```

```bash
docker run --rm layers-demo:broken ls -l /tmp/big.bin 2>&1 || true
```

## Troubleshoot it

```bash
docker image history --format '{{.Size}}\t{{.CreatedBy}}' layers-demo:broken
```

## Fix it

```bash
cat fixed/Dockerfile
docker build -q -t layers-demo:fixed fixed > /dev/null
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.Size}}' layers-demo
```

## Practice challenge

```bash
a=$(docker image inspect --format '{{index .RootFS.Layers 0}}' alpine:3.23)
b=$(docker image inspect --format '{{index .RootFS.Layers 0}}' layers-demo:fixed)
echo "alpine: $a"
echo "fixed:  $b"
[ "$a" = "$b" ] && echo "shared base layer: stored once on disk"
```

## Cleanup

```bash
docker image rm -f layers-demo:broken layers-demo:fixed > /dev/null
rm -rf ~/docker-practice/lesson-017
```
