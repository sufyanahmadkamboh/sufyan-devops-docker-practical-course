<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 052 · Network troubleshooting · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
docker network create debug-net > /dev/null
docker run -d --name app --network debug-net -p 8080:8000 python:3.14-slim python -m http.server 8000 --bind 127.0.0.1 > /dev/null
docker ps --filter name=app --format '{{.Names}}: {{.Status}}, {{.Ports}}'
```

## Demonstration

```bash
docker exec app python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000').status)"
```

## Hands-on lab

```bash
docker ps --filter name=app --format '{{.Status}}'
docker port app
```

## Break it

```bash
code=0; curl -s -m 5 http://localhost:8080 > /dev/null || code=$?
echo "curl exit code $code"
[ "$code" -eq 0 ]
```

```bash
docker run --rm --network debug-net busybox:1.37 wget -qO /dev/null -T 5 http://app:8000 2>&1
```

## Troubleshoot it

```bash
docker run --rm --network container:app busybox:1.37 netstat -tln
```

## Fix it

```bash
docker rm -f app > /dev/null
docker run -d --name app --network debug-net -p 8080:8000 python:3.14-slim python -m http.server 8000 --bind 0.0.0.0 > /dev/null
sleep 1
docker run --rm --network container:app busybox:1.37 netstat -tln | grep 8000
echo "from the host: $(curl -s -w '\n%{http_code}' http://localhost:8080 | tail -1)"
docker run --rm --network debug-net busybox:1.37 wget -qO /dev/null -T 5 http://app:8000 && echo "from a container: ok"
```

## Practice challenge

```bash
docker run -d --name app2 -p 8081:80 python:3.14-slim python -m http.server 8000 --bind 0.0.0.0 > /dev/null
sleep 1
echo "published: $(docker port app2)"
echo "listening: $(docker run --rm --network container:app2 busybox:1.37 netstat -tln | grep -o '0.0.0.0:8000')"
docker rm -f app2 > /dev/null
docker run -d --name app2 -p 8081:8000 python:3.14-slim python -m http.server 8000 --bind 0.0.0.0 > /dev/null
sleep 1
echo "fixed: $(curl -s -w '\n%{http_code}' http://localhost:8081 | tail -1)"
```

## Cleanup

```bash
docker rm -f app app2 > /dev/null
docker network rm debug-net > /dev/null
```
