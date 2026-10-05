# Final exam · instructor solution

> For instructors, and for learners **after** their attempt. Every step is run by the course's tests, so these
> commands produce a 13/13 score on a fresh exam.

<!-- test: contains=exam ready -->
```bash
bash 22-capstone/final-exam/start-exam.sh
cd ~/docker-practice/exam
```

## Task 1 · Inspect a container

<!-- test: contains=nginx:1.30-alpine; output -->
```bash
docker inspect --format '{{.Config.Image}} {{json .HostConfig.PortBindings}}' exam-web
docker port exam-web
```

```text
nginx:1.30-alpine {"80/tcp":[{"HostIp":"","HostPort":"8090"}]}
80/tcp -> 0.0.0.0:8090
80/tcp -> [::]:8090
```

<!-- test -->
```bash
printf 'web_image=nginx:1.30-alpine\nweb_port=8090\n' >> answers.txt
```

Expected reasoning: `.Config.Image` is what the container was created from; the **host** port is the left side of the
port binding (`HostPort`), not the container's port 80.

## Task 2 · Inspect an image

<!-- test: contains=docker-entrypoint.sh; output -->
```bash
docker image inspect --format '{{json .Config.Entrypoint}} {{json .Config.Cmd}}' redis:8-alpine
```

```text
["docker-entrypoint.sh"] ["redis-server"]
```

<!-- test -->
```bash
echo 'redis_entrypoint=docker-entrypoint.sh' >> answers.txt
```

## Task 3 · Why the container exits

<!-- test: contains=127; output -->
```bash
docker ps -a --filter name=exam-worker --format '{{.Names}}: {{.Status}}'
docker logs exam-worker 2>&1
```

```text
exam-worker: Exited (127) 4 seconds ago
worker starting
sh: pyhton: not found
```

Exit code 127 is the shell's "command not found": the command is misspelled (`pyhton`), and the image has no Python at
all (troubleshooting problem 02).

<!-- test -->
```bash
echo 'worker_exit_code=127' >> answers.txt
```

## Task 4 · Logs

<!-- test: contains=/data/orders.db; output -->
```bash
docker logs exam-api 2>&1
```

```text
boot ok
ERROR: cannot open /data/orders.db: permission denied
```

The error goes to standard error; `docker logs` shows both streams (`2>&1` keeps both in a pipe).

<!-- test -->
```bash
echo 'api_error_file=/data/orders.db' >> answers.txt
```

## Task 5 · Networking

<!-- test: contains=exam-back exam-front; output -->
```bash
docker inspect --format '{{range $n, $_ := .NetworkSettings.Networks}}{{$n}} {{end}}' exam-cache exam-client
docker network connect exam-back exam-client
docker inspect --format '{{range $n, $_ := .NetworkSettings.Networks}}{{$n}} {{end}}' exam-client
```

```text
exam-back 
exam-front 
exam-back exam-front 
```

The two containers were on different user-defined networks. `docker network connect` adds a network to a running
container, without recreating it (lesson 048).

## Task 6 · Connectivity

<!-- test: contains=+PONG; output -->
```bash
docker exec exam-client sh -c "printf 'PING\r\n' | nc -w 2 exam-cache 6379"
```

```text
+PONG
```

<!-- test -->
```bash
echo 'cache_reply=+PONG' >> answers.txt
```

The name `exam-cache` resolves through Docker's embedded DNS, which works only on a shared user-defined network.

## Task 7 · Volume

Copy the note out first, then recreate the container with the volume:

<!-- test: contains=remember the milk; output -->
```bash
docker cp exam-notes:/data/note.txt ./note.txt
docker rm -f exam-notes > /dev/null
docker volume create exam-notes-data > /dev/null
docker run --rm -v exam-notes-data:/data -v "$(pwd):/backup" alpine:3.23 cp /backup/note.txt /data/note.txt
docker run -d --name exam-notes -v exam-notes-data:/data alpine:3.23 sleep 3600 > /dev/null
docker exec exam-notes cat /data/note.txt
```

```text
remember the milk
```

## Task 8 · Environment variable

<!-- test: contains=GREETING is not set; output -->
```bash
docker logs exam-greeter 2>&1
```

```text
ERROR: GREETING is not set
```

<!-- test: contains=greeter started; retry=5 -->
```bash
docker rm -f exam-greeter > /dev/null
docker run -d --name exam-greeter -e GREETING="Hello from the exam" exam-greeter:1.0 > /dev/null
sleep 1
docker logs exam-greeter
```

## Task 9 · Optimize the Dockerfile

A multi-stage build: compile in the Go image, ship only the static binary (lessons 087, 089):

<!-- test: contains=exam-optimized -->
```bash
cat > optimize/Dockerfile <<'EOF'
FROM golang:1.26-alpine AS build
WORKDIR /src
COPY go.mod ./
COPY *.go ./
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/go-api .

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /out/go-api /go-api
EXPOSE 8080
ENTRYPOINT ["/go-api"]
EOF
docker build -q -t exam-optimized:1.0 optimize > /dev/null
docker image ls --format '{{.Repository}}:{{.Tag}} {{.Size}}' exam-optimized
```

## Task 10 · Remove privileges

<!-- test: contains=uid=10001 -->
```bash
cat > rootapp/Dockerfile <<'EOF'
FROM python:3.14-alpine
RUN adduser -D -H -u 10001 web
WORKDIR /srv
COPY index.html .
USER web
EXPOSE 8000
CMD ["python", "-m", "http.server", "8000"]
EOF
docker build -q -t exam-nonroot:1.0 rootapp > /dev/null
docker run --rm --entrypoint id exam-nonroot:1.0
```

Port 8000 is above 1024, so the unprivileged user can listen on it without any capability (lesson 081).

## Tasks 11 and 12 · Compose deployment with healthchecks

<!-- test: contains=Healthy -->
```bash
cat > compose/compose.yaml <<'EOF'
services:
  api:
    build: .
    environment:
      REDIS_HOST: redis
    ports: ["127.0.0.1:8091:8000"]
    depends_on:
      redis: { condition: service_healthy }
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"]
      interval: 5s
      timeout: 3s
      retries: 5
  redis:
    image: redis:8-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
EOF
cd compose
docker compose -p exam up -d --build --wait 2>&1 | tail -2
cd ..
```

<!-- test: contains=visits; retry=5 -->
```bash
curl -s http://localhost:8091/visits
```

`--wait` already proved task 12: it returns only when every service is healthy. Check it directly:

<!-- test: contains=healthy; output -->
```bash
(cd compose && docker compose -p exam ps --format '{{.Service}}: {{.Status}}')
```

```text
api: Up 6 seconds (healthy)
redis: Up 12 seconds (healthy)
```

## Task 13 · Registry

<!-- test: contains="1.0" -->
```bash
docker run -d --name exam-registry -p 5000:5000 registry:3 > /dev/null
sleep 2
docker tag exam-optimized:1.0 localhost:5000/exam/optimized:1.0
docker push -q localhost:5000/exam/optimized:1.0 > /dev/null
curl -s http://localhost:5000/v2/exam/optimized/tags/list
```

## Grade

<!-- test: contains=score: 13/13; output -->
```bash
bash ~/docker-practice/exam/check-exam.sh
```

```text
PASS  task  1  inspect a container: image and host port of exam-web
score: 13/13
```

## Cleanup

<!-- test -->
```bash
docker rm -f exam-web exam-worker exam-api exam-cache exam-client exam-notes exam-greeter exam-registry > /dev/null 2>&1 || true
(cd ~/docker-practice/exam/compose && docker compose -p exam down -v --rmi local > /dev/null 2>&1) || true
docker network rm exam-front exam-back > /dev/null 2>&1 || true
docker volume rm exam-notes-data > /dev/null 2>&1 || true
docker image rm -f exam-greeter:1.0 exam-optimized:1.0 exam-nonroot:1.0 localhost:5000/exam/optimized:1.0 > /dev/null 2>&1 || true
rm -rf ~/docker-practice/exam
echo "exam removed"
```
