# Lesson 049 · Container-to-container communication

> Level 8 · Networking · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

Real applications are several containers: an API and its cache, a worker and its queue. They talk to each other over a
shared user-defined network, using the **container name** as the host name and the **container port** (the port the
service listens on inside its container). Publishing with `-p` is only for traffic from outside Docker. Configuration
tells each service where its dependencies are, usually through environment variables such as `REDIS_HOST=redis`.

## Visual

```text
   your computer                     cafe-net (user-defined bridge)
  ┌─────────────┐   -p 8080:5000   ┌───────────────────────┐   redis:6379   ┌──────────────────┐
  │ curl        │ ───────────────▶ │ api  (Flask/gunicorn) │ ─────────────▶ │ redis            │
  │ localhost:  │                  │ listens on 5000       │  name + the    │ listens on 6379  │
  │ 8080        │                  │ REDIS_HOST=redis      │  container port│ not published    │
  └─────────────┘                  └───────────────────────┘                └──────────────────┘
        outside Docker: host port            inside Docker: container name + container port
```

## Lab setup

The Flask API of the course: `/visits` increments a counter in Redis at `REDIS_HOST`.

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-049 examples/python-api
cd ~/docker-practice/lesson-049
printf 'FROM python:3.14-slim\nWORKDIR /app\nCOPY . .\nRUN pip install --no-cache-dir -r requirements.txt\nCMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]\n' > Dockerfile
docker build -q -t cafe-api:1.0 . > /dev/null
```

## Demonstration

One network, the cache, then the API configured to find the cache by name:

<!-- test: contains=api; contains=redis -->
```bash
docker network create cafe-net > /dev/null
docker run -d --name redis --network cafe-net redis:8-alpine > /dev/null
docker run -d --name api --network cafe-net -e REDIS_HOST=redis -p 8080:5000 cafe-api:1.0 > /dev/null
docker ps --format '{{.Names}}: {{.Ports}}'
```

Call the API twice from your computer. Each call makes the API talk to Redis:

<!-- test: contains=visits; output; retry=10 -->
```bash
curl -s http://localhost:8080/visits
curl -s http://localhost:8080/visits
```

```text
{"visits":1}
{"visits":2}
```

The counter lives in Redis, so it keeps counting across calls. Redis itself is not published at all: only `api` can
reach it.

<!-- test: contains=PONG; output -->
```bash
docker exec api python -c "import redis; print(redis.Redis(host='redis').ping() and 'PONG')"
```

```text
PONG
```

## Command breakdown

| Part | What it does |
|---|---|
| `--network cafe-net` | both containers on one user-defined network, so names resolve |
| `--name redis` | the container name is also its DNS name on the network |
| `-e REDIS_HOST=redis` | configuration: where the API finds Redis (lesson 059) |
| `-p 8080:5000` | publish the API's container port 5000 on the host's port 8080 |
| `redis:6379` | container-to-container: the name and the **container** port, never the host port |

## Hands-on lab

**Instructions.** Show that Redis really holds the counter: read the key `visits` with `redis-cli` inside the `redis`
container, then call the API once more and read it again.

**Expected result.** The value grows by one.

**Verification.**

<!-- test: contains=before; contains=after -->
```bash
echo "before: $(docker exec redis redis-cli get visits)"
curl -s http://localhost:8080/visits > /dev/null
echo "after:  $(docker exec redis redis-cli get visits)"
```

## Break it

A teammate deploys a second instance of the API with the cache's host name from another environment, `cache`:

<!-- test -->
```bash
docker run -d --name api2 --network cafe-net -e REDIS_HOST=cache -p 8081:5000 cafe-api:1.0 > /dev/null
```

<!-- test: contains=ok; retry=10 -->
```bash
curl -s http://localhost:8081/health
```

The API is up and healthy. Now the endpoint that needs Redis (`-m 10`: give up after 10 seconds):

<!-- test: anyof=HTTP 000||HTTP 500; output -->
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

<!-- test: fail; anyof=Name or service not known||Temporary failure in name resolution; output=tail:1 -->
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

<!-- test: contains=REDIS_HOST=cache; output -->
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

<!-- test: contains=visits; output; retry=10 -->
```bash
docker rm -f api2 > /dev/null
docker run -d --name api2 --network cafe-net -e REDIS_HOST=redis -p 8081:5000 cafe-api:1.0 > /dev/null
curl -s http://localhost:8081/visits
```

```text
{"visits":4}
```

Both API instances now share the same counter in Redis.

## Practice challenge

Keep `REDIS_HOST=cache` but make it work **without** renaming anything: give the `redis` container the additional
DNS name `cache` on `cafe-net` (a network alias), then start an API with `REDIS_HOST=cache` on port 8082.

<details>
<summary>Solution</summary>

<!-- test: contains=visits; output; retry=10 -->
```bash
docker network disconnect cafe-net redis
docker network connect --alias cache cafe-net redis
docker run -d --name api3 --network cafe-net -e REDIS_HOST=cache -p 8082:5000 cafe-api:1.0 > /dev/null
sleep 2
curl -s http://localhost:8082/visits
```

```text
{"visits":5}
```

An alias is an extra DNS name on one network. Compose uses the service name as an alias in the same way (lesson 065).

</details>

## Real-world example

A team's API calls a payment service and a cache. Each dependency's address is an environment variable
(`PAYMENT_URL=http://payments:8000`, `REDIS_HOST=redis`), and every environment provides the right values: on a laptop
the names of local containers, in production the names of managed services. The image never changes; only the
configuration does.

## Recap

- Containers on a shared user-defined network reach each other by **name** and **container port**.
- `-p` is only for traffic from outside Docker; internal services such as Redis need no published port.
- Pass dependency addresses as configuration (`-e REDIS_HOST=redis`); a 500 with a name-resolution error in the logs
  means the configured name does not exist on the network.
- Network aliases add extra DNS names to a container.

## Cleanup

<!-- test -->
```bash
docker rm -f api api2 api3 redis > /dev/null
docker network rm cafe-net > /dev/null
docker image rm -f cafe-api:1.0 > /dev/null
rm -rf ~/docker-practice/lesson-049
```

Next: [Lesson 050 · Container DNS](../050-container-dns/README.md)
