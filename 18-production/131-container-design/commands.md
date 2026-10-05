<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 131 · Container design · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Demonstration

```bash
docker run --rm nginx:1.30-alpine ls -l /var/log/nginx
```

```bash
docker run -d --name web -p 8080:80 nginx:1.30-alpine > /dev/null
docker ps --filter name=web --format '{{.Names}} {{.Image}} {{.Status}}'
```

```bash
curl -sI http://localhost:8080/ | head -1
docker logs web 2>/dev/null | grep '"HEAD / HTTP'
```

```bash
docker top web -o pid,args
```

```bash
docker rm -f web > /dev/null
docker run -d --name web -p 8080:80 nginx:1.30-alpine > /dev/null
sleep 1
curl -sI http://localhost:8080/ | head -1
```

## Hands-on lab

```bash
curl -sI http://localhost:8080/missing.html | head -1
docker logs web 2>/dev/null | grep missing.html
```

## Break it

```bash
docker run -d --name worker alpine:3.23 sh -c 'while true; do echo "$(date +%T) order processed" >> /var/log/app.log; sleep 1; done' > /dev/null
sleep 3
docker logs worker
echo "lines in docker logs: $(docker logs worker 2>&1 | wc -l | tr -d ' ')"
```

## Troubleshoot it

```bash
docker exec worker tail -n 2 /var/log/app.log
```

## Fix it

```bash
docker rm -f worker > /dev/null
docker run -d --name worker alpine:3.23 sh -c 'ln -sf /dev/stdout /var/log/app.log; while true; do echo "$(date +%T) order processed" >> /var/log/app.log; sleep 1; done'
sleep 3
docker logs worker | tail -n 2
```

## Practice challenge

```bash
curl -s http://localhost:8080/nothing-here.html > /dev/null
docker logs web 2>&1 > /dev/null | grep nothing-here
```

## Cleanup

```bash
docker rm -f web worker > /dev/null
```
