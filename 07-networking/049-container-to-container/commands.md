<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 049 · Container-to-container communication · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-049 examples/python-api
cd ~/docker-practice/lesson-049
printf 'FROM python:3.14-slim\nWORKDIR /app\nCOPY . .\nRUN pip install --no-cache-dir -r requirements.txt\nCMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]\n' > Dockerfile
docker build -q -t cafe-api:1.0 . > /dev/null
```

## Demonstration

```bash
docker network create cafe-net > /dev/null
docker run -d --name redis --network cafe-net redis:8-alpine > /dev/null
docker run -d --name api --network cafe-net -e REDIS_HOST=redis -p 8080:5000 cafe-api:1.0 > /dev/null
docker ps --format '{{.Names}}: {{.Ports}}'
```

```bash
curl -s http://localhost:8080/visits
curl -s http://localhost:8080/visits
```

```bash
docker exec api python -c "import redis; print(redis.Redis(host='redis').ping() and 'PONG')"
```

## Hands-on lab

```bash
echo "before: $(docker exec redis redis-cli get visits)"
curl -s http://localhost:8080/visits > /dev/null
echo "after:  $(docker exec redis redis-cli get visits)"
```

## Break it

```bash
docker run -d --name api2 --network cafe-net -e REDIS_HOST=cache -p 8081:5000 cafe-api:1.0 > /dev/null
```

```bash
curl -s http://localhost:8081/health
```

```bash
curl -s -m 10 -w '\nHTTP %{http_code}\n' http://localhost:8081/visits | tail -1
```

## Troubleshoot it

```bash
docker exec api2 python -c "import os, socket; socket.getaddrinfo(os.environ['REDIS_HOST'], 6379)" 2>&1
```

```bash
docker network inspect cafe-net --format '{{range .Containers}}{{.Name}} {{end}}'
docker inspect api2 --format '{{range .Config.Env}}{{println .}}{{end}}' | grep REDIS_HOST
```

## Fix it

```bash
docker rm -f api2 > /dev/null
docker run -d --name api2 --network cafe-net -e REDIS_HOST=redis -p 8081:5000 cafe-api:1.0 > /dev/null
curl -s http://localhost:8081/visits
```

## Practice challenge

```bash
docker network disconnect cafe-net redis
docker network connect --alias cache cafe-net redis
docker run -d --name api3 --network cafe-net -e REDIS_HOST=cache -p 8082:5000 cafe-api:1.0 > /dev/null
sleep 2
curl -s http://localhost:8082/visits
```

## Cleanup

```bash
docker rm -f api api2 api3 redis > /dev/null
docker network rm cafe-net > /dev/null
docker image rm -f cafe-api:1.0 > /dev/null
rm -rf ~/docker-practice/lesson-049
```
