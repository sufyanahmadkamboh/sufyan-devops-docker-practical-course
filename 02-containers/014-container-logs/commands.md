<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 014 · Container logs · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Demonstration

```bash
docker run -d --name orders alpine:3.23 sh -c '
  for i in 1 2 3 4 5; do echo "order $i accepted"; done
  echo "payment service unreachable" >&2
  exit 1' > /dev/null
sleep 1
echo done
```

```bash
docker logs orders
```

```bash
docker logs --tail 2 -t orders
```

```bash
docker logs orders 2>&1 > /dev/null
```

```bash
docker logs -f web
```

```bash
docker run -d --name web -p 8080:80 nginx:1.30-alpine > /dev/null
curl -s --retry 10 --retry-all-errors --retry-delay 1 http://localhost:8080/ > /dev/null
curl -s http://localhost:8080/missing > /dev/null
docker logs web 2>/dev/null | tail -2
```

## Hands-on lab

```bash
docker logs web 2>/dev/null | grep '"GET /missing' | grep -c ' 404 '
```

## Break it

```bash
docker run -d --name filelogger alpine:3.23 sh -c 'while true; do echo "$(date) heartbeat" >> /var/log/app.log; sleep 1; done' > /dev/null
sleep 2
echo "log lines: $(docker logs filelogger 2>&1 | wc -l | tr -d ' ')"
```

## Troubleshoot it

```bash
docker exec filelogger tail -2 /var/log/app.log
```

## Fix it

```bash
docker run --rm nginx:1.30-alpine ls -l /var/log/nginx/
```

```bash
docker rm -f filelogger > /dev/null
docker run -d --name filelogger alpine:3.23 sh -c 'while true; do echo "$(date) heartbeat"; sleep 1; done' > /dev/null 2>&1 || true
sleep 2
docker logs --tail 1 filelogger
```

## Practice challenge

```bash
docker run -d --name crasher alpine:3.23 sh -c 'echo "loading config /etc/app/config.yml"; cat /etc/app/config.yml'
```

```bash
sleep 1
docker logs crasher
docker inspect --format 'exit code {{.State.ExitCode}}' crasher
```

## Cleanup

```bash
docker rm -f orders web filelogger crasher > /dev/null
```
