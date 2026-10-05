<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 093 · Running is not healthy · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-093 14-observability/093-running-is-not-healthy/examples/single 14-observability/093-running-is-not-healthy/examples/threaded
cd ~/docker-practice/lesson-093
grep -n "sleep\|HTTPServer(" single/app.py
```

## Demonstration

```bash
docker build -q -t cafe-api:single single > /dev/null
docker run -d --name api --restart always -p 8080:8080 cafe-api:single > /dev/null && echo "started api"
```

```bash
curl -s http://localhost:8080/health
docker ps --filter name=api --format '{{.Names}}: {{.Status}}'
```

## Hands-on lab

```bash
docker inspect --format 'state={{.State.Status}} health={{.State.Health.Status}} restarts={{.RestartCount}}' api
```

## Break it

```bash
curl -s -m 2 http://localhost:8080/report || echo "gave up after 2 seconds"
```

## Troubleshoot it

```bash
curl -s -m 2 http://localhost:8080/health || echo "no answer from /health"
```

```bash
docker inspect --format 'state={{.State.Status}} health={{.State.Health.Status}} restarts={{.RestartCount}}' api
```

```bash
docker inspect --format '{{range .State.Health.Log}}{{.Output}}{{end}}' api | grep . | tail -1
```

## Fix it

```bash
docker restart api > /dev/null && echo "restarted"
```

```bash
docker inspect --format 'state={{.State.Status}} health={{.State.Health.Status}}' api
```

```bash
docker rm -f api > /dev/null
docker build -q -t cafe-api:threaded threaded > /dev/null
docker run -d --name api --restart always -p 8080:8080 cafe-api:threaded > /dev/null && echo "started api"
```

```bash
docker inspect --format 'health={{.State.Health.Status}}' api
```

```bash
curl -s -m 2 http://localhost:8080/report || echo "/report gave up after 2 seconds"
curl -s -m 2 http://localhost:8080/health > /dev/null && echo "/health still ok"
```

## Practice challenge

```bash
docker run -d --name api-single -p 8081:8080 cafe-api:single > /dev/null && echo "started api-single"
```

```bash
docker inspect --format '{{.State.Health.Status}}' api-single
```

```bash
curl -s -m 2 http://localhost:8081/report || echo "gave up"
```

```bash
docker ps --filter health=unhealthy --format '{{.Names}}'
```

```bash
docker ps --filter health=unhealthy --format '{{.Names}}' | xargs -r docker restart
```

## Cleanup

```bash
docker rm -f api api-single > /dev/null 2>&1 || true
docker image rm -f cafe-api:single cafe-api:threaded > /dev/null
cd ~ && rm -rf ~/docker-practice/lesson-093
```
