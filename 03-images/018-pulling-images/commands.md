<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 018 · Pulling images · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Demonstration

```bash
docker image ls --digests alpine
```

```bash
docker image pull alpine:3.23 2>&1 || echo "the pull failed: read the error above"
```

```bash
docker image pull mirror.gcr.io/library/busybox:1.37
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.ID}}' | grep busybox
```

```bash
digest=$(docker image inspect --format '{{index .RepoDigests 0}}' alpine:3.23)
echo "$digest"
docker run --rm "$digest" cat /etc/alpine-release
```

## Hands-on lab

```bash
docker image pull -q mirror.gcr.io/library/alpine:3.23
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.ID}}' | grep alpine
docker image rm mirror.gcr.io/library/alpine:3.23
docker image ls --format '{{.Repository}}:{{.Tag}}' alpine
```

## Break it

```bash
docker image pull cafe-menu-api:1.0 2>&1
```

## Troubleshoot it

```bash
docker image inspect docker.io/library/cafe-menu-api:1.0 > /dev/null 2>&1 || echo "no local image docker.io/library/cafe-menu-api:1.0"
```

## Fix it

```bash
docker image inspect busybox:1.37 > /dev/null 2>&1 || docker image pull busybox:1.37
echo "busybox ready: $(docker image inspect --format '{{.Id}}' busybox:1.37 | cut -c1-19)"
```

## Practice challenge

```bash
digest=$(docker image inspect --format '{{index .RepoDigests 0}}' alpine:3.23)
for name in alpine:3.23 docker.io/library/alpine:3.23 "$digest"; do
  docker image inspect --format '{{.Id}}' "$name"
done | sort -u | wc -l | grep -q '^ *1$' && echo "one ID: the same image"
```

## Cleanup

```bash
docker image rm mirror.gcr.io/library/busybox:1.37 > /dev/null
```
