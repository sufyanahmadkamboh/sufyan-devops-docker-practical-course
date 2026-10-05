<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 011 · Running Nginx · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-011 examples/site
cd ~/docker-practice/lesson-011
ls
```

## Demonstration

```bash
docker run -d --name web nginx:1.30-alpine
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
```

```bash
docker logs web 2>&1
```

```bash
ip=$(docker inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' web)
echo "web has the IP address $ip"
docker run --rm alpine:3.23 wget -qO- "http://$ip" | grep '<title>'
```

```bash
docker cp index.html web:/usr/share/nginx/html/index.html
docker cp styles.css web:/usr/share/nginx/html/styles.css
docker run --rm alpine:3.23 wget -qO- "http://$(docker inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' web)" | grep '<h1>'
```

## Hands-on lab

```bash
docker run -d --name web-2 nginx:1.29-alpine > /dev/null 2>&1 || true
docker run --rm alpine:3.23 wget -qS -O /dev/null "http://$(docker inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' web-2)" 2>&1 | grep Server
```

## Break it

```bash
curl -sS http://localhost:8080
```

## Troubleshoot it

```bash
docker ps --filter name=^web$ --format '{{.Names}}: {{.Ports}}'
```

## Fix it

```bash
docker rm -f web > /dev/null
docker run -d --name web -p 8080:80 nginx:1.30-alpine > /dev/null
docker cp index.html web:/usr/share/nginx/html/index.html
docker cp styles.css web:/usr/share/nginx/html/styles.css
docker ps --filter name=^web$ --format '{{.Names}}: {{.Ports}}'
```

```bash
curl -s http://localhost:8080 | grep '<h1>'
```

## Practice challenge

```bash
curl -sI http://localhost:8080/styles.css | grep -i '^content-type'
```

```bash
docker stop web > /dev/null && docker start web > /dev/null
curl -s http://localhost:8080 | grep '<h1>'
```

## Cleanup

```bash
docker rm -f web web-2 > /dev/null
rm -rf ~/docker-practice/lesson-011
```
