<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 056 · Inspecting volumes · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
printf 'FROM alpine:3.23\nVOLUME /data\nCMD ["sh", "-c", "echo \\"entry $(date +%%s)\\" >> /data/log.txt; cat /data/log.txt"]\n' | docker build -q -t journal:1.0 - > /dev/null
docker image inspect journal:1.0 --format '{{json .Config.Volumes}}'
```

## Demonstration

```bash
docker volume create --label team=cafe orders > /dev/null
docker volume inspect orders
```

```bash
docker volume ls --filter label=team=cafe
```

```bash
docker run --name journal-1 journal:1.0 > /dev/null
docker inspect journal-1 --format '{{range .Mounts}}{{.Type}} {{.Name}} -> {{.Destination}}{{end}}'
```

```bash
volume=$(docker inspect journal-1 --format '{{range .Mounts}}{{.Name}}{{end}}')
docker run --rm -v "$volume:/data:ro" alpine:3.23 du -sh /data
```

## Hands-on lab

```bash
docker volume inspect orders --format '{{.CreatedAt}} {{.Driver}}'
docker ps -a --filter volume="$(docker inspect journal-1 --format '{{range .Mounts}}{{.Name}}{{end}}')" --format '{{.Names}}'
```

## Break it

```bash
docker rm journal-1 > /dev/null
docker run --name journal-2 journal:1.0
```

## Troubleshoot it

```bash
docker volume ls --filter dangling=true
```

```bash
for v in $(docker volume ls -q --filter dangling=true); do
  echo "$v: $(docker run --rm -v "$v:/data:ro" alpine:3.23 sh -c 'ls /data 2>/dev/null')"
done
```

## Fix it

```bash
old=$(for v in $(docker volume ls -q --filter dangling=true); do
  docker run --rm -v "$v:/data:ro" alpine:3.23 test -f /data/log.txt && echo "$v"
done | head -1)
docker run --rm -v "$old:/from:ro" -v journal-data:/to alpine:3.23 cp -a /from/. /to/
docker rm journal-2 > /dev/null
docker run --rm -v journal-data:/data journal:1.0
```

## Practice challenge

```bash
docker system df -v | grep -A6 '^Local Volumes space usage:'
```

## Cleanup

```bash
docker volume rm orders journal-data > /dev/null
docker volume prune -f > /dev/null
docker image rm -f journal:1.0 > /dev/null
```
