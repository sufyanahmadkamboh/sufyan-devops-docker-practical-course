<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 051 · EXPOSE vs publishing ports · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Demonstration

```bash
docker image inspect nginx:1.30-alpine --format '{{json .Config.ExposedPorts}}'
```

```bash
docker network create port-net > /dev/null
docker run -d --name hidden --network port-net nginx:1.30-alpine > /dev/null
docker run --rm --network port-net busybox:1.37 wget -qO /dev/null http://hidden && echo "from a container: ok"
docker port hidden || true
```

```bash
docker run -d --name shown --network port-net -p 8080:80 nginx:1.30-alpine > /dev/null
docker port shown
```

```bash
curl -s http://localhost:8080 | grep -o '<title>.*</title>'
```

## Hands-on lab

```bash
docker run -d --name random-port -P nginx:1.30-alpine > /dev/null && echo "started"
```

```bash
port=$(docker port random-port 80/tcp | head -1 | sed 's/.*://')
echo "nginx is on host port $port"
curl -s "http://localhost:$port" | grep -o '<title>.*</title>'
```

## Break it

```bash
printf 'FROM nginx:1.30-alpine\nEXPOSE 80\n' | docker build -q -t my-site:1.0 - > /dev/null
docker run -d --name my-site my-site:1.0 > /dev/null
code=0; curl -s -m 5 http://localhost:80 > /dev/null || code=$?
echo "curl exit code $code"
[ "$code" -eq 0 ]
```

## Troubleshoot it

```bash
echo "published: $(docker port my-site)"
echo "exposed:   $(docker inspect my-site --format '{{json .Config.ExposedPorts}}')"
docker ps --filter name=my-site --format 'PORTS column: {{.Ports}}'
```

## Fix it

```bash
docker rm -f my-site > /dev/null
docker run -d --name my-site -p 127.0.0.1:8081:80 my-site:1.0 > /dev/null
docker port my-site
curl -s http://127.0.0.1:8081 | grep -o '<title>.*</title>'
```

## Practice challenge

```bash
docker run -d --name two-ports -p 8082:80 -p 127.0.0.1:8083:80 nginx:1.30-alpine > /dev/null
docker port two-ports
```

## Cleanup

```bash
docker rm -f hidden shown random-port my-site two-ports > /dev/null
docker network rm port-net > /dev/null
docker image rm -f my-site:1.0 > /dev/null
```
