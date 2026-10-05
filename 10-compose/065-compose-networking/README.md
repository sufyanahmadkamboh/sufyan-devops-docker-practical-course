# Lesson 065 · Networking in Compose

> Level 11 · Docker Compose · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

Compose creates a network for every project (`PROJECT_default`) and attaches every service to it. On that network,
each **service name is a DNS name**: the API reaches Redis at `redis`, not at an IP address. You can also declare your
own networks and attach each service only where it belongs, so a front-end component cannot reach the database at all.

## Visual

```text
 your computer :8080
        │
        ▼
 ┌──────────────── network lesson-065_frontend ────────────────┐
 │   tools (alpine)                    api ─────────────────────┼──┐
 └──────────────────────────────────────────────────────────────┘  │ api is on both networks
 ┌──────────────── network lesson-065_backend ─────────────────┐   │
 │   redis  ◀── "redis:6379" ─────────────── api ◀──────────────┼───┘
 └──────────────────────────────────────────────────────────────┘
   tools → redis: no route, no name (different network)
   inside a container, "localhost" is that container itself
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-065 examples/python-api
cp -r 10-compose/065-compose-networking/examples/. ~/docker-practice/lesson-065/
cd ~/docker-practice/lesson-065
cat compose.yaml
```

## Demonstration

Start the project and look at the networks Compose created:

<!-- test: contains=lesson-065_backend; output -->
```bash
docker compose up -d --build --quiet-build 2> /dev/null
docker network ls --filter name=lesson-065 --format '{{.Name}}  driver={{.Driver}}'
```

```text
lesson-065_backend  driver=bridge
lesson-065_frontend  driver=bridge
```

Which containers are on which network:

<!-- test: contains=redis; output -->
```bash
for net in frontend backend; do
  echo "$net: $(docker network inspect lesson-065_$net --format '{{range .Containers}}{{.Name}} {{end}}')"
done
```

```text
frontend: lesson-065-api-1 lesson-065-tools-1 
backend: lesson-065-api-1 lesson-065-redis-1 
```

The API resolves `redis` through Docker's built-in DNS, and the request works:

<!-- test: contains=redis; output -->
```bash
docker compose exec api python -c "import socket; print('redis ->', socket.gethostbyname('redis'))"
```

```text
redis -> 172.18.0.2
```

<!-- test: retry=15; contains=visits; output -->
```bash
curl -s localhost:8080/visits
```

```text
{"visits":1}
```

The `tools` container is not on `backend`: Redis does not exist for it.

<!-- test: fail; contains=bad address; output -->
```bash
docker compose exec tools ping -c 1 -W 2 redis 2>&1
```

```text
ping: bad address 'redis'
```

## Command breakdown

| Key / command | What it does |
|---|---|
| `networks:` (top level) | declare networks; Compose names them `PROJECT_NAME` |
| `networks: [a, b]` (service) | attach the service to these networks (instead of `default`) |
| service name | the DNS name of the service on every network it is attached to |
| `docker network inspect NET --format '{{range .Containers}}…'` | the containers on a network |
| `docker compose exec SERVICE CMD` | run a command in the service's container (lesson 072) |

## Hands-on lab

**Instructions.** Find the IP addresses of the `api` container: it has one per network.

**Expected result.** Two addresses, one on `lesson-065_backend`, one on `lesson-065_frontend`.

**Verification.**

<!-- test: contains=lesson-065_backend; contains=lesson-065_frontend -->
```bash
docker inspect lesson-065-api-1 --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{$net.IPAddress}}{{"\n"}}{{end}}'
```

## Break it

A colleague "fixed" a connection problem on their laptop by pointing the API at `localhost`, in an override file
(Compose merges `-f` files in order, later ones win):

<!-- test: contains=500; output -->
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

<!-- test: contains=Connection refused; output -->
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

<!-- test: retry=15; contains=visits -->
```bash
docker compose up -d 2> /dev/null
docker compose exec api printenv REDIS_HOST
curl -s localhost:8080/visits
```

## Practice challenge

Without editing `compose.yaml`, prove that `tools` can reach the API but not Redis: from `tools`, call the API's
`/health` endpoint on port 5000, then try Redis's port 6379.

<details>
<summary>Solution</summary>

<!-- test: contains=ok; contains=bad address; output -->
```bash
cd ~/docker-practice/lesson-065
docker compose exec tools wget -qO- http://api:5000/health; echo
docker compose exec tools nc -z -w 2 redis 6379 2>&1 || echo "redis unreachable"
```

```text
{"status":"ok"}

nc: bad address 'redis'
redis unreachable
```

Inside the network, services talk on their **container** ports (5000), not on the published host ports (8080). The
`frontend` network has no way to Redis: separating networks limits what a compromised front-end container can reach.

</details>

## Real-world example

A typical stack puts the reverse proxy on a `frontend` network, the database on a `backend` network, and only the API
on both. A vulnerability in the proxy then cannot be used to connect to the database directly. The capstone project
uses exactly this layout.

## Recap

- Compose creates `PROJECT_default` and attaches every service; custom `networks:` give finer control.
- Service names are DNS names on every network the service joins.
- Services talk on container ports; published ports are only for your computer.
- `localhost` inside a container is the container itself.

## Cleanup

<!-- test -->
```bash
cd ~/docker-practice/lesson-065
docker compose down -v --rmi local 2> /dev/null
rm -rf ~/docker-practice/lesson-065
```

The lab folder is gone: go back to the course folder (`cd` to where you cloned the course) before the next lesson.

Next: [Lesson 066 · Volumes in Compose](../066-compose-volumes/README.md)
