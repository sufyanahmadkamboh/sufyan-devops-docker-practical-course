<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 062 · Why Docker Compose? · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

The manual way fails as soon as one step is forgotten. Start a second copy of the API by hand, on the right network,
but forget `-p`:

```bash
docker run -d --name forgetful --network lesson-062_default -e REDIS_HOST=redis lesson-062-api > /dev/null
sleep 2
curl -s -w '\nHTTP %{http_code}\n' localhost:8081/visits | tail -1
test "${PIPESTATUS[0]}" -eq 0
```

```text
HTTP 000
```

## Troubleshoot it

`HTTP 000` means curl got no HTTP answer at all: nothing listens on port 8081 of your computer. The container is
running; check which of its ports are published:

```bash
docker ps --filter name=forgetful --format '{{.Names}}  ports: {{.Ports}}'
```

```text
forgetful  ports: 5000/tcp
```

`5000/tcp` without `0.0.0.0:…->` means the port exists inside the container but is not published to the host
(lesson 012). One forgotten flag out of many: that is what Compose prevents.

## Fix it

Do not repeat long `docker run` commands by hand: let Compose apply the file every time.

```bash
docker rm -f forgetful > /dev/null
curl -s localhost:8080/visits
```

The Compose service gets the same ports, network and variables on every `up`, for every developer.
