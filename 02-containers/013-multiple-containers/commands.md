<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 013 · Running multiple containers · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Demonstration

```bash
for site in a b; do
  port=$([ "$site" = a ] && echo 8080 || echo 8081)
  docker run -d --name "site-$site" --label project=lesson-013 -p "$port:80" nginx:1.30-alpine \
    sh -c "echo '<h1>Site $site</h1>' > /usr/share/nginx/html/index.html && exec nginx -g 'daemon off;'" > /dev/null
done
docker run -d --name cache --label project=lesson-013 redis:8-alpine > /dev/null
echo done
```

```bash
curl -s http://localhost:8080
curl -s http://localhost:8081
```

```bash
docker ps --filter label=project=lesson-013 --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}'
```

```bash
docker stop $(docker ps -q --filter label=project=lesson-013) > /dev/null
echo "running: $(docker ps -q --filter label=project=lesson-013 | wc -l | tr -d ' ')"
docker start $(docker ps -aq --filter label=project=lesson-013) > /dev/null
echo "running: $(docker ps -q --filter label=project=lesson-013 | wc -l | tr -d ' ')"
```

## Hands-on lab

```bash
docker run -d --name site-c --label project=lesson-013 -p 8082:80 nginx:1.30-alpine \
  sh -c "echo '<h1>Site c</h1>' > /usr/share/nginx/html/index.html && exec nginx -g 'daemon off;'"
```

```bash
curl -s http://localhost:8082
docker ps -q --filter label=project=lesson-013 | wc -l | tr -d ' '
```

## Break it

```bash
docker stop $(docker ps -q --filter label=project=lesson-999) 2>&1
```

## Troubleshoot it

```bash
echo "matches: $(docker ps -q --filter label=project=lesson-999 | wc -l | tr -d ' ')"
```

## Fix it

```bash
ids=$(docker ps -q --filter label=project=lesson-999)
if [ -n "$ids" ]; then docker stop $ids; else echo "nothing to stop"; fi
```

## Practice challenge

```bash
for i in 1 2 3 4 5; do
  docker run -d --name "web-$i" --label project=load-test -p "809$i:80" nginx:1.30-alpine > /dev/null
done
```

```bash
ok=0
for i in 1 2 3 4 5; do curl -sf "http://localhost:809$i" > /dev/null && ok=$((ok + 1)); done
echo "$ok of 5 answered"
```

```bash
echo "removed: $(docker rm -f $(docker ps -aq --filter label=project=load-test) | wc -l | tr -d ' ')"
```

## Cleanup

```bash
docker rm -f $(docker ps -aq --filter label=project=lesson-013) > /dev/null
```
