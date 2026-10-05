<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 021 · The danger of the latest tag · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-021
cd ~/docker-practice/lesson-021
printf 'FROM alpine:3.23\nARG VERSION\nRUN echo "cafe menu $VERSION" > /version\nCMD ["sleep", "3600"]\n' > Dockerfile
```

## Demonstration

```bash
docker build -q --build-arg VERSION=1.0 -t cafe-menu . > /dev/null
docker image ls --format '{{.Repository}}:{{.Tag}}' cafe-menu
```

```bash
docker image ls --format '{{.Repository}}:{{.Tag}}' nginx
docker image inspect nginx > /dev/null 2>&1 || echo "Error: No such image: nginx (= nginx:latest)"
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-021
docker run -d --name menu-a cafe-menu > /dev/null
docker container inspect --format '{{.Image}}' menu-a
docker exec menu-a cat /version
```

## Break it

```bash
docker build -q --build-arg VERSION=2.0 -t cafe-menu . > /dev/null
docker run -d --name menu-b cafe-menu > /dev/null
echo "menu-a: $(docker exec menu-a cat /version)"
echo "menu-b: $(docker exec menu-b cat /version)"
```

## Troubleshoot it

```bash
docker container ls --format '{{.Names}}  name={{.Image}}' --filter name=menu-
for c in menu-a menu-b; do echo "$c runs $(docker container inspect --format '{{.Image}}' $c | cut -c1-19)"; done
echo "cafe-menu:latest is now $(docker image inspect --format '{{.Id}}' cafe-menu:latest | cut -c1-19)"
```

## Fix it

```bash
docker build -q --build-arg VERSION=2.0 -t cafe-menu:2.0 . > /dev/null
docker run -d --name menu-v2 cafe-menu:2.0 > /dev/null
echo "menu-v2: $(docker exec menu-v2 cat /version)"
```

## Practice challenge

```bash
docker image ls --format '{{.Repository}}:{{.Tag}}' python
docker image inspect python:latest > /dev/null 2>&1 || echo "python:latest is not local: FROM python would pull it"
echo "FROM python" | sed 's/^FROM python$/FROM python:3.14-slim/'
```

## Cleanup

```bash
docker rm -f menu-a menu-b menu-v2 > /dev/null
docker image rm -f cafe-menu:latest cafe-menu:2.0 > /dev/null
docker image prune -f > /dev/null
rm -rf ~/docker-practice/lesson-021
```
