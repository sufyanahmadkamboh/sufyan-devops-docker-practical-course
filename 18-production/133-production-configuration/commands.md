<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 133 · Production configuration · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-133 examples/node-api
cp 18-production/130-production-dockerfile/examples/final/Dockerfile 18-production/130-production-dockerfile/examples/final/.dockerignore ~/docker-practice/lesson-133/
cp 18-production/133-production-configuration/examples/default.conf ~/docker-practice/lesson-133/
cd ~/docker-practice/lesson-133
docker build -q -t node-api:1.0 . > /dev/null
```

## Demonstration

```bash
docker run -d --name api-staging -p 8081:3000 -e GREETING="Hello from staging" -e APP_VERSION=1.0 node-api:1.0 > /dev/null
docker run -d --name api-production -p 8082:3000 -e GREETING="Hello from production" -e APP_VERSION=1.0 node-api:1.0 > /dev/null
docker ps --filter name=api- --format '{{.Names}}'
```

```bash
curl -s http://localhost:8081/ && echo
curl -s http://localhost:8082/ && echo
docker inspect api-staging api-production --format '{{.Name}} {{.Image}}'
```

```bash
docker run -d --name web -p 8080:80 -v "$(pwd)/default.conf:/etc/nginx/conf.d/default.conf:ro" nginx:1.30-alpine > /dev/null
docker ps --filter name=web --format '{{.Names}} {{.Image}}'
```

```bash
curl -sI http://localhost:8080/ | grep -i x-environment
curl -s http://localhost:8080/health
```

```bash
mkdir -p secrets && printf 'example-api-key-change-me' > secrets/api_key
docker run -d --name env-secret -e API_KEY=example-api-key-change-me alpine:3.23 sleep 300 > /dev/null
docker run -d --name file-secret -v "$(pwd)/secrets/api_key:/run/secrets/api_key:ro" alpine:3.23 sleep 300 > /dev/null
docker inspect env-secret --format '{{range .Config.Env}}{{println .}}{{end}}' | grep API_KEY
docker inspect file-secret --format '{{range .Config.Env}}{{println .}}{{end}}' | grep -c API_KEY || true
docker exec file-secret cat /run/secrets/api_key && echo
```

## Hands-on lab

```bash
docker run -d --name api-dev -p 8083:3000 -e GREETING="Hello from dev" -e APP_VERSION=dev node-api:1.0 > /dev/null
sleep 1
curl -s http://localhost:8083/ && echo
[ "$(docker inspect api-dev --format '{{.Image}}')" = "$(docker inspect api-production --format '{{.Image}}')" ] && echo "same image"
```

## Break it

```bash
docker rm -f web > /dev/null
docker run -d --name web -p 8080:80 -v "$(pwd)/default.conf:/etc/nginx/default.conf:ro" nginx:1.30-alpine > /dev/null
sleep 1
curl -s http://localhost:8080/ | grep "<title>"
curl -sI http://localhost:8080/ | grep -ci x-environment || true
```

## Troubleshoot it

```bash
docker inspect web --format '{{range .Mounts}}mounted at {{.Destination}} (writable: {{.RW}}){{println}}{{end}}'
docker exec web nginx -T 2>/dev/null | grep "configuration file"
```

## Fix it

```bash
docker rm -f web > /dev/null
docker run -d --name web -p 8080:80 -v "$(pwd)/default.conf:/etc/nginx/conf.d/default.conf:ro" nginx:1.30-alpine > /dev/null
sleep 1
docker exec web nginx -T 2>/dev/null | grep "configuration file /etc/nginx/conf.d/default.conf"
curl -sI http://localhost:8080/ | grep -i x-environment
```

## Practice challenge

```bash
docker exec web sh -c 'echo "# changed" >> /etc/nginx/conf.d/default.conf' 2>&1 || true
```

## Cleanup

```bash
docker rm -f api-staging api-production api-dev web env-secret file-secret > /dev/null
docker image rm -f node-api:1.0 > /dev/null
rm -rf ~/docker-practice/lesson-133
```
