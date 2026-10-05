<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 104 · Multi-architecture images · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-104 16-advanced/104-multi-architecture-images/examples
cd ~/docker-practice/lesson-104
cat Dockerfile
```

## Demonstration

```bash
docker buildx inspect --bootstrap | grep -i '^platforms'
```

```bash
docker buildx build -q --platform linux/amd64,linux/arm64 -t cafe-hello:1.0 --load . > /dev/null
docker image ls cafe-hello --format '{{.Repository}}:{{.Tag}}'
```

```bash
docker image ls --tree cafe-hello
```

```bash
docker run --rm cafe-hello:1.0
docker run --rm --platform linux/arm64 cafe-hello:1.0
```

## Hands-on lab

```bash
docker buildx build -q --platform linux/arm64 -t cafe-hello:arm --load . > /dev/null
docker image inspect --format '{{.Os}}/{{.Architecture}}' cafe-hello:arm
```

## Break it

```bash
docker run --rm --platform linux/arm/v7 cafe-hello:1.0 2>&1
```

## Troubleshoot it

```bash
docker image ls --tree cafe-hello
```

## Fix it

```bash
docker buildx build -q --platform linux/amd64,linux/arm64,linux/arm/v7 -t cafe-hello:1.0 --load . > /dev/null
docker image ls --tree cafe-hello
```

## Practice challenge

```bash
awk '/^RUN CGO_ENABLED/ {
  print "ARG BUILDPLATFORM TARGETPLATFORM"
  print "RUN echo \"BUILDPLATFORM=$BUILDPLATFORM TARGETPLATFORM=$TARGETPLATFORM uname=$(uname -m)\""
} { print }' Dockerfile > Dockerfile.debug
docker buildx build --no-cache --progress plain --platform linux/arm64 -f Dockerfile.debug -t cafe-hello:debug . 2>&1 |
  grep -o 'BUILDPLATFORM=.*uname=[a-z0-9_]*$' | head -1
```

## Cleanup

```bash
docker image rm -f cafe-hello:1.0 cafe-hello:arm cafe-hello:debug > /dev/null 2>&1 || true
docker buildx prune -f > /dev/null
cd ~ && rm -rf ~/docker-practice/lesson-104
```
