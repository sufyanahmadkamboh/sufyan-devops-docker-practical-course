<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 020 · Image tags · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-020
cd ~/docker-practice/lesson-020
printf 'FROM alpine:3.23\nARG VERSION\nRUN echo "cafe menu $VERSION" > /version\nCMD ["cat", "/version"]\n' > Dockerfile
cat Dockerfile
```

## Demonstration

```bash
docker build -q --build-arg VERSION=1.4.2 -t cafe-menu:1.4.2 . > /dev/null
docker image tag cafe-menu:1.4.2 cafe-menu:1.4
docker image tag cafe-menu:1.4.2 cafe-menu:1
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.ID}}' cafe-menu
```

```bash
docker build -q --build-arg VERSION=1.4.3 -t cafe-menu:1.4.3 . > /dev/null
docker image tag cafe-menu:1.4.3 cafe-menu:1.4
docker image tag cafe-menu:1.4.3 cafe-menu:1
for tag in 1.4.2 1.4.3 1.4 1; do echo "cafe-menu:$tag → $(docker run --rm cafe-menu:$tag)"; done
```

```bash
docker image tag cafe-menu:1.4.3 localhost:5000/cafe/menu:1.4.3
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.ID}}' localhost:5000/cafe/menu
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-020
docker build -q --build-arg VERSION=1.4.4 -t cafe-menu:1.4.4 -t cafe-menu:1.4 -t cafe-menu:1 . > /dev/null
[ "$(docker image ls -q cafe-menu:1.4.4)" = "$(docker image ls -q cafe-menu:1)" ] && echo "one ID for 1.4.4, 1.4 and 1"
```

## Break it

```bash
docker image tag cafe-menu:1.4.4 Menu-Board:1.0
```

## Troubleshoot it

```bash
for name in Menu-Board:1.0 menu-board:1.0+build7 menu-board:1.0-build7; do
  if docker image tag cafe-menu:1.4.4 "$name" 2> /dev/null; then echo "valid:   $name"; else echo "invalid: $name"; fi
done
```

## Fix it

```bash
docker image tag cafe-menu:1.4.4 menu-board:1.0
docker image ls --format '{{.Repository}}:{{.Tag}}' menu-board
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-020
docker build -q --build-arg VERSION=1.5.0 -t cafe-menu:1.5.0 -t cafe-menu:1.5 -t cafe-menu:1 . > /dev/null
for tag in 1.4 1.5 1; do echo "$tag → $(docker run --rm cafe-menu:$tag)"; done
```

## Cleanup

```bash
docker image rm $(docker image ls --format '{{.Repository}}:{{.Tag}}' | grep -e '^cafe-menu:' -e '^menu-board:' -e '^localhost:5000/cafe/menu:') > /dev/null
rm -rf ~/docker-practice/lesson-020
```
