<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 059 · Environment variables · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-059 examples/node-api
cd ~/docker-practice/lesson-059
grep -n 'process.env' server.js
```

## Demonstration

```bash
docker run --rm node:24-alpine env | sort
```

```bash
docker run -d --name default-api -p 8080:3000 -v "$(pwd):/app:ro" -w /app node:24-alpine node server.js > /dev/null
docker run -d --name configured-api -p 8081:3000 -v "$(pwd):/app:ro" -w /app \
  -e GREETING="Welcome to the cafe" -e APP_VERSION=1.4.0 node:24-alpine node server.js > /dev/null
sleep 1
curl -s http://localhost:8080; echo
curl -s http://localhost:8081; echo
```

```bash
export TABLE=12
docker run --rm -e TABLE alpine:3.23 sh -c 'echo "table $TABLE"'
```

## Hands-on lab

```bash
docker inspect configured-api --format '{{range .Config.Env}}{{println .}}{{end}}'
docker run -d --name port-api -p 8082:4000 -e PORT=4000 -v "$(pwd):/app:ro" -w /app node:24-alpine node server.js > /dev/null
sleep 1
curl -s http://localhost:8082 > /dev/null && docker logs port-api
```

## Break it

```bash
docker run -d --name db postgres:18-alpine > /dev/null
sleep 2
docker ps -a --filter name=db --format '{{.Names}}: {{.Status}}'
```

## Troubleshoot it

```bash
docker logs db 2>&1
```

## Fix it

```bash
docker rm db > /dev/null
docker run -d --name db -e POSTGRES_PASSWORD=example-password-change-me postgres:18-alpine > /dev/null
sleep 3
docker exec db pg_isready -h 127.0.0.1 -U postgres
```

## Practice challenge

```bash
port=8083
for envname in dev staging production; do
  docker run -d --name "api-$envname" -p "$port:3000" -v "$(pwd):/app:ro" -w /app \
    -e GREETING="Hello from $envname" -e APP_VERSION="1.4.0-$envname" node:24-alpine node server.js > /dev/null
  port=$((port + 1))
done
sleep 1
for port in 8083 8084 8085; do curl -s "http://localhost:$port"; echo; done
```

## Cleanup

```bash
docker rm -f default-api configured-api port-api db api-dev api-staging api-production > /dev/null
rm -rf ~/docker-practice/lesson-059
```
