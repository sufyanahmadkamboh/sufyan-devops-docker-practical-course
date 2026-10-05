<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 075 · What is a registry? · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
docker run -d --name registry -p 5000:5000 registry:3 > /dev/null
sleep 2
docker inspect registry --format '{{.Name}}: {{.State.Status}}'
```

## Demonstration

```bash
docker tag alpine:3.23 localhost:5000/cafe/alpine:3.23
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.ID}}' | grep alpine
```

```bash
docker push localhost:5000/cafe/alpine:3.23
```

```bash
curl -s localhost:5000/v2/_catalog
curl -s localhost:5000/v2/cafe/alpine/tags/list
```

```bash
docker image rm localhost:5000/cafe/alpine:3.23 > /dev/null
docker pull localhost:5000/cafe/alpine:3.23
```

## Hands-on lab

```bash
docker tag busybox:1.37 localhost:5000/tools/busybox:1.37
docker push -q localhost:5000/tools/busybox:1.37
curl -s localhost:5000/v2/_catalog
```

## Break it

```bash
docker pull localhost:5000/cafe/alpine:3.24 2>&1
```

## Troubleshoot it

```bash
curl -s localhost:5000/v2/cafe/alpine/tags/list
```

## Fix it

```bash
docker pull -q localhost:5000/cafe/alpine:3.23
```

## Practice challenge

```bash
docker tag localhost:5000/cafe/alpine:3.23 localhost:5000/cafe/alpine:stable
docker push -q localhost:5000/cafe/alpine:stable > /dev/null
accept='Accept: application/vnd.oci.image.index.v1+json, application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.v2+json'
a=$(curl -sI -H "$accept" localhost:5000/v2/cafe/alpine/manifests/3.23 | grep -i docker-content-digest | tr -d '\r')
b=$(curl -sI -H "$accept" localhost:5000/v2/cafe/alpine/manifests/stable | grep -i docker-content-digest | tr -d '\r')
echo "$a"; echo "$b"
[ "$a" = "$b" ] && echo "same digest"
```

## Cleanup

```bash
docker rm -f registry > /dev/null
docker image rm localhost:5000/cafe/alpine:3.23 localhost:5000/cafe/alpine:stable localhost:5000/tools/busybox:1.37 > /dev/null
```
