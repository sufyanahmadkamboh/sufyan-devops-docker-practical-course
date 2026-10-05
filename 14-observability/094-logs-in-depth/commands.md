<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 094 · Logs in depth · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-094 14-observability/094-logs-in-depth/examples
cd ~/docker-practice/lesson-094
cat worker.py
```

## Demonstration

```bash
docker run -d --name web -p 8080:80 nginx:1.30-alpine > /dev/null && echo "started web"
```

```bash
curl -s -w '\n%{http_code}\n' http://localhost:8080/ | tail -n 1
curl -s -w '\n%{http_code}\n' http://localhost:8080/missing | tail -n 1
```

```bash
docker logs -t --tail 2 web
```

```bash
echo "stdout lines: $(docker logs web 2>/dev/null | wc -l)"
echo "stderr lines: $(docker logs web 2>&1 >/dev/null | wc -l)"
```

```bash
docker logs --since 1m web 2>/dev/null
```

## Hands-on lab

```bash
docker run -d --name ticker alpine:3.23 sh -c 'for i in 1 2 3; do echo "tick $i"; sleep 1; done' > /dev/null
docker logs -f -t ticker
```

## Break it

```bash
docker run -d --name worker -v "$(pwd)/worker.py:/worker.py:ro" python:3.14-alpine python /worker.py > /dev/null && echo "started worker"
```

```bash
sleep 4
docker logs worker
```

## Troubleshoot it

```bash
docker top worker -o pid,args
```

```bash
docker run -d --name worker-tty -t -v "$(pwd)/worker.py:/worker.py:ro" python:3.14-alpine python /worker.py > /dev/null
sleep 2
docker logs worker-tty | head -2
docker rm -f worker-tty > /dev/null
```

## Fix it

```bash
docker rm -f worker > /dev/null
docker run -d --name worker -e PYTHONUNBUFFERED=1 -v "$(pwd)/worker.py:/worker.py:ro" python:3.14-alpine python /worker.py > /dev/null && echo "started worker"
```

```bash
sleep 3
docker logs worker | head -5
```

## Practice challenge

```bash
echo "failed orders: $(docker logs worker 2>&1 >/dev/null | wc -l)"
docker logs -t worker 2>&1 >/dev/null | tail -1
```

## Cleanup

```bash
docker rm -f web worker worker-tty ticker > /dev/null 2>&1 || true
cd ~ && rm -rf ~/docker-practice/lesson-094
```
