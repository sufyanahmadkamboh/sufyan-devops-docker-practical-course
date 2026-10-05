# Troubleshooting problem 09 · DNS failure between containers

> ⏱ 15 minutes · run every command from the course folder · related lessons: 047, 048, 050

## Problem

Two containers started with plain `docker run`, no network options. The API cannot reach `cache` by name, but a
colleague notices that the same command with the cache's IP address works.

## Symptoms

<!-- test -->
```bash
docker run -d --name cache redis:8-alpine > /dev/null
docker run -d --name api redis:8-alpine sleep 3600 > /dev/null
```

<!-- test: fail; contains=Name does not resolve; output -->
```bash
docker exec api redis-cli -h cache ping 2>&1
```

```text
Could not connect to Redis at cache:6379: Name does not resolve
```

## Investigation

**1. Same network?** Both are on `bridge`, the default network:

<!-- test: contains=bridge; output -->
```bash
for c in api cache; do
  echo "$c: $(docker inspect --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{.IPAddress}}{{end}}' $c)"
done
```

```text
api: bridge 172.17.0.3
cache: bridge 172.17.0.2
```

**2. Does the network path work, without DNS?**

<!-- test: contains=PONG; output -->
```bash
ip=$(docker inspect --format '{{.NetworkSettings.Networks.bridge.IPAddress}}' cache)
docker exec api redis-cli -h "$ip" ping
```

```text
PONG
```

The network is fine: only **name resolution** fails.

**3. Which DNS server does the container ask?**

<!-- test: contains=nameserver; output -->
```bash
docker exec api grep nameserver /etc/resolv.conf
```

```text
nameserver 192.168.65.7
```

On the default bridge, a container gets a copy of the host's DNS configuration: that server knows public names, not
container names.

## Commands

| Command | What it tells you |
|---|---|
| `docker exec NAME cat /etc/resolv.conf` | the DNS server the container uses (`127.0.0.11` = Docker's embedded DNS) |
| `docker exec NAME getent hosts OTHER` | whether a name resolves (no output = it does not) |
| test with the IP address | separates "network unreachable" from "name not resolvable" |

## Output interpretation

- `Name does not resolve` with a working IP connection is a DNS problem, not a routing problem.
- The default `bridge` network has **no container DNS** (a legacy behaviour kept for compatibility, lesson 047).
  User-defined networks get Docker's embedded DNS server at `127.0.0.11`, which resolves container names and
  network aliases (lesson 050).
- IP addresses on a bridge change whenever a container is recreated: never configure them by hand.
- Other causes of the same message: a typo in the name, or the containers are on different networks
  ([problem 08](../08-wrong-network/README.md)).

## Root cause

Both containers are on the default bridge network, where Docker does not resolve container names.

## Fix

Use a user-defined network for every application:

<!-- test -->
```bash
docker rm -f api cache > /dev/null
docker network create shop > /dev/null
docker run -d --name cache --network shop redis:8-alpine > /dev/null
docker run -d --name api --network shop redis:8-alpine sleep 3600 > /dev/null
```

## Verification

<!-- test: retry=5; contains=PONG; contains=127.0.0.11; output -->
```bash
docker exec api grep nameserver /etc/resolv.conf
docker exec api redis-cli -h cache ping
```

```text
nameserver 127.0.0.11
PONG
```

## Prevention

- Never rely on the default bridge for applications: create a network (`docker network create`) or use Compose,
  which creates one per project automatically (lesson 065).
- Refer to services by name, never by IP address.
- `--link` is the deprecated workaround for the default bridge: do not use it in new setups.

## Cleanup

<!-- test -->
```bash
docker rm -f api cache > /dev/null
docker network rm shop > /dev/null
```

Next: [Problem 10 · Database connection failure](../10-database-connection-failure/README.md)
