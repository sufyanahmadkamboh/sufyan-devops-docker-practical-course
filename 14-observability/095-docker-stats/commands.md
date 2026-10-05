<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 095 · docker stats · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Demonstration

```bash
docker run -d --name web nginx:1.30-alpine > /dev/null
docker run -d --name cache --memory 64m redis:8-alpine redis-server --enable-debug-command local > /dev/null
echo "started web and cache"
```

```bash
docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.PIDs}}' web cache
```

## Hands-on lab

```bash
docker stats --no-stream --format '{{.MemPerc}} {{.Name}}' | sort -rn
```

## Break it

```bash
docker run -d --name worker alpine:3.23 sh -c 'while :; do :; done' > /dev/null && echo "started worker"
```

## Troubleshoot it

```bash
sleep 3
docker stats --no-stream --format '{{.CPUPerc}} {{.Name}}' | sort -rn | head -1
```

```bash
docker top worker -o pid,args
```

## Fix it

```bash
docker update --cpus 0.2 worker
```

```bash
sleep 3
docker stats --no-stream --format '{{.CPUPerc}} {{.Name}}' worker
```

```bash
docker rm -f worker > /dev/null
docker run -d --name worker --cpus 0.5 alpine:3.23 sh -c 'while :; do sleep 1; done' > /dev/null
docker stats --no-stream --format '{{.CPUPerc}} {{.Name}}' worker
```

## Practice challenge

```bash
docker exec cache redis-cli DEBUG POPULATE 550000
```

```bash
docker stats --no-stream --format '{{.Name}} {{.MemPerc}}' | tr -d '%' |
  awk '$2 > 50 { print "WARNING " $1 " uses " $2 "% of its memory limit" }'
```

## Cleanup

```bash
docker rm -f web cache worker > /dev/null 2>&1 || true
```
