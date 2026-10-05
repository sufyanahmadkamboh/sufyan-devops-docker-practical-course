<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 012 · Port mapping · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Demonstration

```bash
docker run -d --name web-a -p 8080:80 nginx:1.30-alpine > /dev/null
docker run -d --name web-b -p 8081:80 nginx:1.29-alpine > /dev/null
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}'
```

```bash
curl -sI http://localhost:8080 | grep -i '^server'
curl -sI http://localhost:8081 | grep -i '^server'
```

```bash
docker port web-a
```

```bash
docker run -d --name admin -p 127.0.0.1:8082:80 nginx:1.30-alpine > /dev/null
docker port admin
```

## Hands-on lab

```bash
docker run -d --name cache -p 127.0.0.1:6380:6379 redis:8-alpine > /dev/null
docker port cache
```

## Break it

```bash
docker run -d --name web-c -p 8080:80 nginx:1.30-alpine 2>&1
```

## Troubleshoot it

```bash
docker ps --filter publish=8080 --format '{{.Names}} owns {{.Ports}}'
```

## Fix it

```bash
docker rm web-c > /dev/null
docker run -d --name web-c -p 8083:80 nginx:1.30-alpine > /dev/null
docker port web-c
```

## Practice challenge

```bash
docker run -d --name temp -p 80 nginx:1.30-alpine
```

```bash
port=$(docker port temp 80/tcp | head -1 | sed 's/.*://')
echo "Docker chose host port $port"
curl -s "http://localhost:$port" | grep '<title>'
```

## Cleanup

```bash
docker rm -f web-a web-b web-c admin cache temp > /dev/null
```
