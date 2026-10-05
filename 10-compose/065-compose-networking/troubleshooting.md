<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 065 · Networking in Compose · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A colleague "fixed" a connection problem on their laptop by pointing the API at `localhost`, in an override file
(Compose merges `-f` files in order, later ones win):

```bash
cat broken/compose.override.yaml
docker compose -f compose.yaml -f broken/compose.override.yaml up -d 2> /dev/null
sleep 3
curl -s -w '\nHTTP %{http_code}\n' localhost:8080/visits | tail -1
```

```text
# a "quick fix" a colleague committed: connect to Redis on localhost
services:
  api:
    environment:
      REDIS_HOST: localhost
HTTP 500
```

## Troubleshoot it

The API answers, but `/visits` fails. Read the API's log, then check what `localhost` means inside the container:

```bash
docker compose logs api 2>&1 | grep -o "redis.exceptions.ConnectionError.*" | tail -1
docker compose exec api python -c "import socket; print('localhost ->', socket.gethostbyname('localhost'))"
```

```text
redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379. Connection refused.
localhost -> 127.0.0.1
```

`localhost` is the API container itself, and nothing listens on port 6379 there. Each container has its own network
stack: Redis is a different container, reachable only by its service name (or IP) on a shared network.

## Fix it

Remove the override, so `REDIS_HOST` is the service name again:

```bash
docker compose up -d 2> /dev/null
docker compose exec api printenv REDIS_HOST
curl -s localhost:8080/visits
```
