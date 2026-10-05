<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 062 · Why Docker Compose? · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-062 examples/python-api
cp -r 10-compose/062-why-compose/examples/. ~/docker-practice/lesson-062/
cd ~/docker-practice/lesson-062
ls
```

## Demonstration

```bash
docker network create cafe
docker build -q -t cafe-api:dev . > /dev/null
docker run -d --name redis --network cafe redis:8-alpine > /dev/null
docker run -d --name api --network cafe -p 8080:5000 -e REDIS_HOST=redis cafe-api:dev > /dev/null
docker ps --format '{{.Names}}'
```

```bash
curl -s localhost:8080/visits
```

```bash
docker rm -f api redis > /dev/null
docker network rm cafe > /dev/null
docker image rm cafe-api:dev > /dev/null
```

```bash
cat compose.yaml
```

```bash
docker compose up -d --build 2>&1 | grep -E "Network|Container"
```

```bash
curl -s localhost:8080/visits
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-062
docker compose ps --format '{{.Service}}: {{.State}}'
docker network ls --filter name=lesson-062 --format '{{.Name}}'
```

## Break it

```bash
docker run -d --name forgetful --network lesson-062_default -e REDIS_HOST=redis lesson-062-api > /dev/null
sleep 2
curl -s -w '\nHTTP %{http_code}\n' localhost:8081/visits | tail -1
test "${PIPESTATUS[0]}" -eq 0
```

## Troubleshoot it

```bash
docker ps --filter name=forgetful --format '{{.Names}}  ports: {{.Ports}}'
```

## Fix it

```bash
docker rm -f forgetful > /dev/null
curl -s localhost:8080/visits
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-062
docker compose down 2>&1 | grep -c Removed
[ -z "$(docker ps -aq --filter label=com.docker.compose.project=lesson-062)" ] && \
  [ -z "$(docker network ls -q --filter name=lesson-062)" ] && echo "nothing left"
```

## Cleanup

```bash
cd ~/docker-practice/lesson-062
docker compose down -v --rmi local 2> /dev/null
rm -rf ~/docker-practice/lesson-062
```
