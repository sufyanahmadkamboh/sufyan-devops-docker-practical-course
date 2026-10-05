<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 049 · Container-to-container communication · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A teammate deploys a second instance of the API with the cache's host name from another environment, `cache`:

```bash
docker run -d --name api2 --network cafe-net -e REDIS_HOST=cache -p 8081:5000 cafe-api:1.0 > /dev/null
```

```bash
curl -s http://localhost:8081/health
```

The API is up and healthy. Now the endpoint that needs Redis (`-m 10`: give up after 10 seconds):

```bash
curl -s -m 10 -w '\nHTTP %{http_code}\n' http://localhost:8081/visits | tail -1
```

```text
HTTP 000
```

## Troubleshoot it

`HTTP 000` after 10 seconds: no answer at all. (On a Linux engine the lookup usually fails at once instead, and you
get `HTTP 500`: the same problem, reported faster.) `/health` works, so the container, the port mapping and the
application are fine; only the part that talks to Redis fails. Test the dependency from **inside** the failing
container, exactly as the application sees it:

```bash
docker exec api2 python -c "import os, socket; socket.getaddrinfo(os.environ['REDIS_HOST'], 6379)" 2>&1
```

```text
...
socket.gaierror: [Errno -2] Name or service not known
```

`Name or service not known` (or `Temporary failure in name resolution`, depending on the host's DNS setup): the
name in `REDIS_HOST` cannot be resolved, and the Redis client keeps retrying, which
is why the request hung (gunicorn kills the stuck worker after 30 seconds: `WORKER TIMEOUT` in `docker logs api2`).
Confirm which names exist on the network and what the container was configured with:

```bash
docker network inspect cafe-net --format '{{range .Containers}}{{.Name}} {{end}}'
docker inspect api2 --format '{{range .Config.Env}}{{println .}}{{end}}' | grep REDIS_HOST
```

```text
redis api2 api 
REDIS_HOST=cache
```

The checklist for "service A cannot reach service B": same network? right name? right **container** port? Is B
listening on `0.0.0.0` (lesson 052)?

## Fix it

Configuration is fixed by recreating the container with the right value (a running container's environment cannot
be changed):

```bash
docker rm -f api2 > /dev/null
docker run -d --name api2 --network cafe-net -e REDIS_HOST=redis -p 8081:5000 cafe-api:1.0 > /dev/null
curl -s http://localhost:8081/visits
```

```text
{"visits":4}
```

Both API instances now share the same counter in Redis.
