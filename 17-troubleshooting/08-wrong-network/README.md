# Troubleshooting problem 08 · Wrong network

> ⏱ 15 minutes · run every command from the course folder · related lessons: 048, 049, 050

## Problem

The application was split into two networks: `frontend` for the public side, `backend` for the data stores. Since
then the API cannot reach its Redis cache by name, although the container `cache` is running.

## Symptoms

Reproduce the setup: Redis on `backend`, the API (here a Redis client container that stays up) on `frontend` only.

<!-- test -->
```bash
docker network create frontend > /dev/null
docker network create backend > /dev/null
docker run -d --name cache --network backend redis:8-alpine > /dev/null
docker run -d --name api --network frontend redis:8-alpine sleep 3600 > /dev/null
```

<!-- test: fail; anyof=Name does not resolve||Try again; output -->
```bash
docker exec api redis-cli -h cache ping 2>&1
```

```text
Could not connect to Redis at cache:6379: Try again
```

## Investigation

**1. Both containers run?**

<!-- test: contains=cache; contains=api; output -->
```bash
docker ps --filter name=cache --filter name=api --format '{{.Names}}: {{.Status}}'
```

```text
api: Up 18 seconds
cache: Up 19 seconds
```

**2. Which networks is each container on?**

<!-- test: contains=frontend; contains=backend; output -->
```bash
for c in api cache; do
  echo "$c: $(docker inspect --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{end}}' $c)"
done
```

```text
api: frontend 
cache: backend 
```

**3. Who is on the backend network?**

<!-- test: contains=cache; output -->
```bash
docker network inspect backend --format '{{range .Containers}}{{.Name}} {{end}}'
```

```text
cache 
```

## Commands

| Command | What it tells you |
|---|---|
| `docker inspect --format '{{range $n, $_ := .NetworkSettings.Networks}}{{$n}} {{end}}' NAME` | the networks of a container |
| `docker network inspect NET --format '{{range .Containers}}{{.Name}} {{end}}'` | the containers on a network |
| `docker exec NAME getent hosts OTHER` (or `nslookup`) | whether a name resolves from that container |

## Output interpretation

Docker's DNS answers names only **within a network**: a container resolves the names of containers that share at
least one network with it (lesson 050). `api` is on `frontend`, `cache` on `backend`; they share none, so for `api`
the name `cache` does not exist, and even its IP address would not be routable. Docker's DNS server does not know the
name, forwards the question to the host's DNS servers, and the client gets either `Name does not resolve` or, when
that forwarded query times out (as above, after several seconds), `Try again`. Either way it is not a
DNS outage ([problem 09](../09-dns-failure/README.md)): it is a missing network membership.

## Root cause

The API needs both networks (public traffic on `frontend`, data stores on `backend`) but was attached to `frontend`
only.

## Fix

Connect the running container to the second network (no restart needed):

<!-- test -->
```bash
docker network connect backend api
```

## Verification

<!-- test: contains=PONG; output -->
```bash
docker exec api redis-cli -h cache ping
docker inspect --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{end}}' api
```

```text
PONG
backend frontend 
```

## Prevention

- Declare networks per service in Compose, so membership is reviewed in code (lesson 065):
  `api: networks: [frontend, backend]`, `cache: networks: [backend]`.
- Keep data stores on an internal network only, and attach exactly the services that need them.
- When a name does not resolve, check network membership first, then the name itself.

## Cleanup

<!-- test -->
```bash
docker rm -f api cache > /dev/null
docker network rm frontend backend > /dev/null
```

Next: [Problem 09 · DNS failure](../09-dns-failure/README.md)
