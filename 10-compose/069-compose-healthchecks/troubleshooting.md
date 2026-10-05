<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 069 · Healthchecks in Compose · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A teammate changes the port the healthcheck uses (`5001` instead of the API's `5000`):

```bash
cp compose.yaml compose.good.yaml
cp broken/compose.yaml compose.yaml
docker compose up -d --wait --wait-timeout 40 2>&1 | tail -1
test "${PIPESTATUS[0]}" -eq 0
```

```text
container lesson-069-api-1 is unhealthy
```

## Troubleshoot it

`unhealthy`, although the API itself works:

```bash
curl -s localhost:8080/health
```

```text
{"status":"ok"}
```

So the check is wrong, not the application. Read what the checks printed:

```bash
docker inspect lesson-069-api-1 --format '{{range .State.Health.Log}}{{.ExitCode}} {{.Output}}{{end}}' | grep -o "ConnectionRefusedError.*" | tail -1
docker inspect lesson-069-api-1 --format '{{json .Config.Healthcheck.Test}}'
```

```text
ConnectionRefusedError: [Errno 111] Connection refused
["CMD","python","-c","import urllib.request; urllib.request.urlopen('http://127.0.0.1:5001/health', timeout=2)"]
```

The check connects to port 5001, where nothing listens. A healthcheck tests the container from **inside**: it must use
the container port the application listens on.

## Fix it

```bash
cp compose.good.yaml compose.yaml
docker compose up -d --wait 2> /dev/null
docker compose ps --format '{{.Service}}: {{.Status}}'
```
