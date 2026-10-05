# Project 03 · Python API with Redis

> ⏱ 1 hour · run every command from the course folder

## Goal

Run the Flask API ([examples/python-api](../../examples/python-api)) the way it runs in production, behind the
Gunicorn application server, together with the Redis database it counts visits in: one Compose file, a healthcheck on
each service, data that survives a restart, and no root user.

## Requirements

- [ ] The API runs under Gunicorn (2 workers), not Flask's development server, as a non-root user
- [ ] Redis and the API are defined in one `compose.yaml`; the API finds Redis by its service name
- [ ] The API starts only when Redis is **healthy**, and has a healthcheck of its own
- [ ] The visit counter survives a restart of Redis (named volume, append-only file)
- [ ] Redis is not published on the host: only the API is reachable from outside

## Architecture

```text
                        Compose project "project03", network project03_default
 curl ──▶ localhost:8083 ──▶ ┌──────────────────────────┐      ┌───────────────────┐
                             │ api (python-api:1.0)     │ ───▶ │ redis             │
                             │ gunicorn, 2 workers      │ DNS  │ redis:8-alpine    │
                             │ user app (10001)  :8000  │ name │ :6379 (not        │
                             └──────────────────────────┘ redis│  published)       │
                                                               └─────────┬─────────┘
                                                                         ▼
                                                                volume redis-data
```

## Build it

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh project-03 examples/python-api
cp -r 21-projects/03-python-api/solution/. ~/docker-practice/project-03/
cd ~/docker-practice/project-03
ls -A
```

<!-- test: contains=gunicorn; output -->
```bash
cat Dockerfile
```

```text
# The Flask API served by Gunicorn (a production WSGI server), as an unprivileged user.
FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
RUN useradd --system --uid 10001 --no-create-home app
USER app
EXPOSE 8000
HEALTHCHECK --interval=5s --timeout=3s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-", "app:app"]
```

<!-- test: contains=service_healthy; output -->
```bash
cat compose.yaml
```

```text
# The Python API and its Redis, as one application.
name: project03

services:
  api:
    build: .
    image: python-api:1.0
    ports: ["8083:8000"]
    environment:
      REDIS_HOST: ${REDIS_HOST:-redis}
      GREETING: Hello from Gunicorn
    depends_on:
      redis: { condition: service_healthy }
    restart: unless-stopped

  redis:
    image: redis:8-alpine
    command: ["redis-server", "--appendonly", "yes"]
    volumes: [redis-data:/data]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
    restart: unless-stopped

volumes:
  redis-data: {}
```

Build and start everything; `--wait` returns when both services are healthy:

<!-- test: contains=Healthy -->
```bash
docker compose up -d --build --wait 2>&1 | tail -3
```

## Verify

<!-- test: contains="status":"ok"; retry=10 -->
```bash
curl -s http://localhost:8083/health
```

<!-- test: contains="visits":3; output -->
```bash
curl -s http://localhost:8083/visits
curl -s http://localhost:8083/visits
curl -s http://localhost:8083/visits
```

```text
{"visits":1}
{"visits":2}
{"visits":3}
```

Gunicorn with two workers, as user `app`:

<!-- test: contains=Booting worker; output -->
```bash
docker compose logs api --no-log-prefix 2>&1 | grep -E "Listening|Booting worker"
docker compose exec api id -un
```

```text
[2026-10-05 12:26:28 +0000] [1] [INFO] Listening at: http://0.0.0.0:8000 (1)
[2026-10-05 12:26:28 +0000] [7] [INFO] Booting worker with pid: 7
[2026-10-05 12:26:28 +0000] [8] [INFO] Booting worker with pid: 8
app
```

Both services healthy, and only the API has a host port:

<!-- test: contains=healthy; output -->
```bash
docker compose ps --format 'table {{.Service}}\t{{.Status}}\t{{.Ports}}'
```

```text
SERVICE   STATUS                    PORTS
api       Up 9 seconds (healthy)    0.0.0.0:8083->8000/tcp, [::]:8083->8000/tcp
redis     Up 15 seconds (healthy)   6379/tcp
```

Restart Redis: the counter continues from where it was, because its data lives in the volume:

<!-- test -->
```bash
docker compose restart redis 2>&1 | tail -1
```

<!-- test: contains="visits":4; retry=10 -->
```bash
curl -s http://localhost:8083/visits
```

## Break it and fix it

A teammate tests the API on their laptop, where Redis runs on the same machine, and deploys with `REDIS_HOST=localhost`:

<!-- test: contains=500; retry=5; output -->
```bash
REDIS_HOST=localhost docker compose up -d --wait 2>&1 | tail -1
curl -s -w '\n%{http_code}\n' http://localhost:8083/visits | tail -n 1
```

```text
 Container project03-api-1 Healthy 
500
```

The API container is up and even **healthy** (its `/health` does not use Redis), but `/visits` fails with 500. The
logs give the reason:

<!-- test: contains=ConnectionError; output -->
```bash
docker compose logs api --no-log-prefix 2>&1 | grep -m1 -E "ConnectionError"
docker compose exec api python -c "import os; print('REDIS_HOST =', os.environ['REDIS_HOST'])"
```

```text
redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379. Connection refused.
REDIS_HOST = localhost
```

Inside a container, `localhost` is the container itself, not the computer and not the other services: nothing listens
on port 6379 in the API's container, so the connection is refused. Other containers are reached by their service
name (`redis`). Fix the configuration, and Compose recreates only the API:

<!-- test: contains="visits"; retry=10 -->
```bash
docker compose up -d --wait 2>&1 | tail -1
curl -s http://localhost:8083/visits
```

A healthcheck that also checks the dependencies would have caught this at start-up; decide per service whether a lost
dependency should make it unhealthy (and restarted) or not (troubleshooting problem 21).

## Stretch goals

- Scale the API to three containers with `docker compose up -d --scale api=3` (remove the fixed host port first, or
  put Nginx in front: project 08).
- Add a `/ready` endpoint that pings Redis, and use it as the healthcheck.
- Limit Redis to 64 MB of memory with `deploy.resources.limits` and `--maxmemory` (module 15).

## Cleanup

<!-- test -->
```bash
cd ~/docker-practice/project-03
docker compose down -v 2>&1 | tail -1
docker image rm -f python-api:1.0 > /dev/null
cd ~ && rm -rf ~/docker-practice/project-03
```

Next: [Project 04 · Go API, as small as it gets](../04-go-api/README.md)
