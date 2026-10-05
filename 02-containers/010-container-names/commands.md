<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 010 · Container names · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Demonstration

```bash
docker run -d nginx:1.30-alpine > /dev/null
docker run -d --name web nginx:1.30-alpine > /dev/null
docker ps --format 'table {{.ID}}\t{{.Names}}\t{{.Image}}'
```

```bash
id=$(docker inspect --format '{{.Id}}' web)
echo "full ID: $id"
[ "$(docker inspect --format '{{.Name}}' "${id:0:4}")" = "/web" ] && echo "the prefix ${id:0:4} and the name web are the same container"
```

```bash
docker rename web proxy
docker ps --filter name=proxy --format '{{.Names}} {{.Status}}'
```

## Hands-on lab

```bash
docker run -d --name cache-1 redis:8-alpine > /dev/null
docker rename cache-1 session-cache
docker ps --filter name=session-cache --format '{{.Names}} {{.ID}}'
```

## Break it

```bash
docker run -d --name proxy nginx:1.30-alpine 2>&1
```

## Troubleshoot it

```bash
docker ps -a --filter name=^proxy$ --format '{{.Names}}: {{.Status}} (created {{.RunningFor}})'
```

## Fix it

```bash
docker rm -f proxy > /dev/null
docker run -d --name proxy nginx:1.30-alpine > /dev/null
docker ps --filter name=^proxy$ --format '{{.Names}}: {{.Status}}'
```

## Practice challenge

```bash
docker run -d --name "my web" nginx:1.30-alpine 2>&1 | head -1
docker run -d --name web.v2_blue-1 nginx:1.30-alpine > /dev/null
docker ps --filter name=web.v2 --format '{{.Names}}'
```

## Cleanup

```bash
docker rm -f $(docker ps -aq --filter ancestor=nginx:1.30-alpine) session-cache > /dev/null
```
